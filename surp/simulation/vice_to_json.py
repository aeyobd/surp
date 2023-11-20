import vice
import pandas as pd
import numpy as np
import random
from os import path
import json
from .._globals import MAX_SF_RADIUS, DATA_DIR

from .vice_utils import load_model, zone_to_R

# these are not used but pickles
# won't behave otherwise
import surp
from surp.simulation import multizone_sim
from surp import yields



def json_output(file_name, isotopic=False, overwrite=False):
    """
    Creates a json object from the given vice_file and then pickles this object
    to store model information in a single file

    TODO: Implement isotopic handling

    """
    name = path.splitext(file_name)[0]
    json_name = f"{name}.json"

    if path.exists(json_name) and not overwrite:
        print("skipping %s, file exists" % json_name)
        return 0


    output = load_model(file_name)
    model = out_to_dict(output)

    # save_result(model, f"{name}.csv")

    with open(json_name, "w") as f:
        json.dump(model, f)
        print("saving to ", json_name)



def out_to_dict(multioutput):
    history, mdf = reduce_history(multioutput)
    stars = pd.DataFrame(multioutput.stars.todict())
    sampled_stars = create_star_sample(stars)

    sampled_stars["MG_H"] = sampled_stars["[mg/h]"]
    sampled_stars["MG_FE"] = sampled_stars["[mg/fe]"]
    sampled_stars["C_MG"] = sampled_stars["[c/mg]"]
    sampled_stars["N_MG"] = sampled_stars["[n/mg]"]
    sampled_stars["C_N"] = sampled_stars["[c/n]"]
    
    return {
        "history": history.to_dict(),
        "mdf": mdf.to_dict(),
        "stars_unsampled": stars.to_dict(),
        "stars": sampled_stars.to_dict()
    }


def reduce_history(multioutput):
    """
    Helper funcion while initializing the class"""
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
    return pd.read_csv(path.join(DATA_DIR, "R_subgiants_cdf.csv"))


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



def save_result(model, filename):
    dist = pd.DataFrame()
    s = model["stars"]["solar"]


    print("saving to ", filename)
    dist.to_csv(filename)



if __name__ == "__main__":
    json_output(sys.argv[1] + "*", json_name=None, isotopic=False, overwrite=False)

