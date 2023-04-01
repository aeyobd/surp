import vice
import pandas as pd
import numpy as np
import random
import os.path
from os.path import exists
import json

from . import multizone_sim
from ..analysis.vice_utils import load_model, show_stars

def json_output(file_name, json_name=None, isotopic=False, overwrite=False):
    """
    Creates a vice_model object from the given vice_file and then pickles this object
    to store model information in a single file

    """
    if json_name is None:
        ext_loc = file_name.rfind(".")
        # these should use os.path isntead
        dir_loc = file_name.rfind("/") + 1
        name = file_name[dir_loc:ext_loc]
        json_name = "%s.json" % name

    if exists(json_name) and not overwrite:
        # raise ValueError("file %s exists and overwrite is not set" % json_name)
        print("skipping %s, file exists" % json_name)
        return 0


    # TODO add isotopic options
    output = load_model(file_name)
    model = model_json(output)

    with open(json_name, "w") as f:
        json.dump(model, f)
        

def model_json(multioutput):
    unsampled_stars = pd.DataFrame(multioutput.stars.todict())
    history, mdf = reduce_history(multioutput)
    unsampled_stars, stars = reduce_stars(multioutput)
    
    stars = {key: value.to_dict() for key, value in stars.items()}
    
    return {
        "history": history.to_dict(),
        "mdf": mdf.to_dict(),
        "stars_unsampled": unsampled_stars.to_dict(),
        "stars": stars
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

    for i in range(200):
        zone = multioutput.zones["zone%i" % i]

        df = pd.DataFrame(zone.history.todict())
        df["R"] = [i/10]*len(df)
        history = pd.concat(history, df, ignore_index=True)

        df = pd.DataFrame(zone.mdf.todict())
        df["R"] = [i/10]*len(df)
        mdf = pd.concat(mdf, df, ignore_index=True)
    
    return history, mdf

def reduce_stars(multioutput):
    """
    Helper function which both
    converts stars from vice.multioutput to 
    a pandas dataframe and samples the stars
    to weight by mass correctly"""

    n_stars = 10_000
    unsampled_stars = pd.DataFrame(multioutput.stars.todict())

    # filter out numerical artifacts
    max_zone = 155
    s = unsampled_stars[unsampled_stars["zone_origin"] < max_zone]
    stars = {}
    stars["all"]= sample_stars(s, n_stars)

    solar_filter = s["r_final"] > 7
    solar_filter &= s["r_final"] < 9
    solar_filter &= s["abs_z"] > 0
    solar_filter &= s["abs_z"] < 0.5
    stars["solar"] = sample_stars(s[solar_filter], n_stars)

    apogee_filter = s["r_final"] > 7
    apogee_filter &= s["r_final"] < 9
    apogee_filter &= s["abs_z"] > 0
    apogee_filter &= s["abs_z"] < 1
    stars["apogee"] = sample_stars(s[apogee_filter], n_stars)
    
    return unsampled_stars, stars


def sample_stars(stars, num=1000):
    r"""
    Samples a population of stars while respecting mass weights

    Parameters
    ----------
    stars: ``pd.DataFrame``
        A dataframe containing stars
        Must have properties ``mass``
    num: ``int`` [default: 1000]
        The number of stars to sample

    Returns
    -------
    A np.array of the sampled parameter from stars
    """

    size = len(stars)
    result = {key: np.zeros(num) for key in stars.keys()}

    index = random.choices(np.arange(size), weights=stars["mass"], k=num)

    return stars.iloc[index].copy()

if __name__ == "__main__":
    json_output(sys.argv[1] + "*", json_name=None, isotopic=False, overwrite=False)
