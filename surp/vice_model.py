import pandas as pd
import json
import numpy as np
import random
import vice
from surp.gce_math import is_high_alpha
import os


import surp
from surp.simulation import multizone_sim
from surp import yields

def R_to_zone(r: float, zone_width):
    return int(np.floor(r/zone_width))

def zone_to_R(zone: int, zone_width):
    return (zone + 1/2) * zone_width


class ViceModel():
    """
    A convineince class which holds and works with VICE multioutputs

    Attributes
    ----------
    history: ``pd.DataFrame``
        Contains a data frame
        See vice.output.history
    mdf: ``pd.DataFrame``
        A dataframe of metallicity distribution functions by radius
    stars: ``pd.DataFrame``
    apogee_stars
    unfiltered_stars
    """

    def __init__(self, stars, history, sampled_stars=None):
        if sampled_stars is None:
            sampled_stars = create_star_sample(stars)
            sampled_stars["MG_H"] = sampled_stars["[mg/h]"]
            sampled_stars["MG_FE"] = sampled_stars["[mg/fe]"]
            sampled_stars["C_MG"] = sampled_stars["[c/mg]"]
            sampled_stars["N_MG"] = sampled_stars["[n/mg]"]
            sampled_stars["C_N"] = sampled_stars["[c/n]"]
        self.stars_unsampled = pd.DataFrame(stars)
        self.stars = pd.DataFrame(sampled_stars)

        self.history = pd.DataFrame(history)

    def rename_columns(self):
        self.history["[fe/o]"] = -self.history["[o/fe]"]
        self.stars["[fe/o]"] = -self.stars["[o/fe]"]


    @classmethod
    def from_saved(cls, filename):
        """
        given the filename, 
        """

        with open(filename, "r") as f:
            d = json.load(f)
        return cls(d["stars_unsampled"], d["history"], d["stars"])

    @classmethod
    def from_vice(self, filename, hydrodiskstars=False, zone_width=0.1):
        name = os.path.splitext(filename)[0]
        json_name = f"{name}.json"
        output = load_vice(filename)
        model = out_to_dict(output)
        history = reduce_history(output)
        stars_unsampled = reduce_stars(output)

        return cls()


    def save(self, filename):
        if os.path.exists(json_name) and not overwrite:
            print("skipping %s, file exists" % json_name)





def reduce_history(multioutput):
    """
    Returns a pandas DF object representing the entire history class
    """
    history_cols = multioutput.zones["zone0"].history.keys()
    history_cols.append("R")
    history = pd.DataFrame(columns=history_cols)

    mdf_cols = multioutput.zones["zone0"].mdf.keys()
    mdf_cols.append("R")
    mdf = pd.DataFrame(columns=mdf_cols)

    keys = multioutput.zones.keys()
    N = len(keys)
    for i in range(N):
        zone = multioutput.zones[keys[i]]

        df = pd.DataFrame(zone.history.todict())
        df["R"] = np.repeat(zone_to_R(i), len(df))
        history = pd.concat((history, df), ignore_index=True)

        df = pd.DataFrame(zone.mdf.todict())
        df["R"] = np.repeat(zone_to_R(i), len(df))
        mdf = pd.concat((mdf, df), ignore_index=True)
    
    return history, mdf



def create_star_sample(stars, num=12000):
    cdf = load_cdf()
    sample = pd.DataFrame(columns=stars.columns)

    for _ in range(num):
        sample = pd.concat((sample, rand_star(stars, cdf)), ignore_index=True)

    return sample


def load_cdf():
    return pd.read_csv(os.path.join(DATA_DIR, "R_subgiants_cdf.csv"))


def rand_zone(cdf):
    p = np.random.rand()
    return cdf.zone.loc[cdf.cdf > p].iloc[0]


def rand_star(stars, cdf):
    return rand_star_in_zone(stars, rand_zone(cdf))


def rand_star_in_zone(stars, zone):
    df = stars.loc[stars.zone_final == zone]

    size = len(df)
    index = random.choices(np.arange(size), weights=df["mass"], k=1)

    return df.iloc[index]



def load_vice(name, hydrodisk=False, zone_width=0.01):
    """Loads a vice.milkyway model output at the location name

    Parameters
    ----------
    name : str
        the name of the model to load
    hydrodisk : bool = False
        if hydrodisk, than reads in abs_z from  analogdata

    Returns
    -------
    vice.multioutput file
    """
    milkyway = vice.output(name)
    if hydrodisk:
        milkyway.stars["abs_z"] = calculate_z(milkyway)
    else:
        milkyway.stars["abs_z"] = [0 for _ in milkyway.stars["zone_origin"]]

    milkyway.stars["R_origin"] = zone_to_R(np.array(milkyway.stars["zone_origin"]), zone_width)
    milkyway.stars["R_final"] = zone_to_R(np.array(milkyway.stars["zone_final"]), zone_width)

    if "[c/o]" not in milkyway.stars.keys():
        milkyway.stars["[c/o]"] = -np.array(milkyway.stars["[o/c]"])
    if "[c/n]" not in milkyway.stars.keys():
        milkyway.stars["[c/n]"] = -np.array(milkyway.stars["[n/c]"])

    o_fe = np.array(milkyway.stars["[o/fe]"])
    fe_h = np.array(milkyway.stars["[fe/h]"])
    milkyway.stars["high_alpha"] = is_high_alpha(o_fe, fe_h)

    return milkyway


def analogdata(filename):
    # from VICE/src/utils
    # last column of analogdata is z_height_final
    data = []
    with open(filename, 'r') as f:
        line = f.readline()
        while line[0] == '#':
            line = f.readline()
        while line != '':
            line = line.split()
            data.append([int(line[0]), float(line[1]), float(line[-1])])
            line = f.readline()
        f.close()
    return data


def calculate_z(output):
    analog_data = analogdata(output.name + "_analogdata.out")
    return [np.abs(row[-1]) for row in analog_data][:output.stars.size[0]]


# 
# def sample_stars(stars, num=1000):
#     r"""
#     Samples a population of stars while respecting mass weights
# 
#     Parameters
#     ----------
#     stars: the stars attribute from vice.output
#     num: (int) the number of stars to sample
# 
#     Returns
#     -------
#     A np.array of the sampled parameter from stars
#     """
# 
#     size = len(stars.todict()["mass"])
#     result = {key: np.zeros(num) for key in stars.keys()}
# 
#     index = random.choices(np.arange(size), weights=stars["mass"], k=num)
#     for i in range(num):
#         for key in stars.keys():
#             result[key][i] = stars[key][index[i]]
#     return vice.dataframe(result)
