import random
import re
import os
import numpy as np
import pandas as pd
import vice

from surp.simulation import multizone_sim
from surp import yields
from surp.gce_math import is_high_alpha
from ._globals import ELEMENTS, DATA_DIR



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

    return milkyway



def reduce_history(multioutput, zone_width=0.1):
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
        df["R"] = np.repeat(zone_to_R(i, zone_width=zone_width), len(df))
        history = pd.concat((history, df), ignore_index=True)

        df = pd.DataFrame(zone.mdf.todict())
        df["R"] = np.repeat(zone_to_R(i, zone_width=zone_width), len(df))
        mdf = pd.concat((mdf, df), ignore_index=True)
    
    return history, mdf



def reduce_stars(multioutput):
    df = pd.DataFrame(multioutput.stars.todict())
    print(df.keys())
    df = rename_columns(df)
    drop_z_cols(df)
    print(df.keys())
    df = order_abundance_ratios(df)
    print(df.keys())
    df["high_alpha"] = is_high_alpha(df.MG_FE, df.MG_H)
    print(df.keys())
    return df


def create_star_sample(stars, num=12000):
    cdf = load_cdf()
    sample = pd.DataFrame(columns=stars.columns)

    for _ in range(num):
        sample = pd.concat((sample, rand_star(stars, cdf)), ignore_index=True)

    return sample


def R_to_zone(r: float, zone_width):
    return int(np.floor(r/zone_width))


def zone_to_R(zone: int, zone_width):
    return (zone + 1/2) * zone_width


def ele_columns():
    cols = []
    N = len(ELEMENTS)

    for i in range(N):
        ele = ELEMENTS[i]
        for j in range(i, N):
            if j == i:
                ele2 = "H"
            else:
                ele2 = ELEMENTS[j]
            cols.append(f"{ele}_{ele2}")
    return cols


def new_name(col):
    new_col = col.upper()
    new_col = new_col.replace("[", "")
    new_col = new_col.replace("]", "")
    new_col = new_col.replace("/", "_")
    return new_col


def invert_name(col):
    eles = extract_eles(col)
    if eles:
        return "%s_%s" % (eles[1], eles[0])
    else:
        raise ValueError("not valid column name", col)

def is_ele(ele):
    if ele.lower() == "h":
        return True
    return ele.lower() in vice.solar_z.keys()

def extract_eles(col):
    matches = col.split("_")
    if ((len(matches) == 2)
        and is_ele(matches[0])
        and is_ele(matches[1])
        ):
        return matches
    return False


def order_abundance_ratios(df):
    cols = df.keys()
    ele_cols = ele_columns()

    for col in ele_cols:
        col2 = invert_name(col)
        if col not in cols:
            if col2 in cols:
                df[col] = -df[col2]
                df.drop(col2, axis=1, inplace=True)
            else:
                print("warning, no data for ", col)
    return df


def is_z_col(col):
    r = re.compile(r"z\([a-z]{1,2}\)")
    return r.match(col)


def drop_z_cols(df):
    for col in df.keys():
        if is_z_col(col):
            df.drop(col, axis=1, inplace=True)



def rename_columns(df):
    new_cols = []
    for col in df.keys():
        if is_abund_ratio(col):
            new_col = new_name(col)
        else:
            new_col = col

        new_cols.append(new_col)

    df.columns = new_cols
    return df
    


def is_abund_ratio(col):
    r = re.compile(r"\[[a-z]{1,2}/[a-z]{1,2}\]")
    if r.match(col):
        return True
    return False




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




def calculate_z(output):
    analog_data = analogdata(output.name + "_analogdata.out")
    return [np.abs(row[-1]) for row in analog_data][:output.stars.size[0]]


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


