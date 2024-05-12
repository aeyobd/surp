import numpy as np
import pickle
import pandas as pd
import os

from . import gce_math as gcem


def vincenzo2021_raw():
    """
    Reads in the CNOdredgeup.obj file 
    from the data in V+21 and returns the file
    as a pandas dataframe with original column
    names
    
    Note: this does not read in the calabration values for C, N, O abundance:

    For solar:
    Log C/H = -3.61
    Log N/H = -4.22
    Log O/H = -3.34

    Also, corrections for O/H are small (<0.02), so
    using magnesium may still be okay.
    """
    script_dir = os.path.dirname(__file__)
    rel_path = "../data/CNOdredgeup.obj"
    abs_path = os.path.join(script_dir, rel_path)
    f = open(abs_path, "rb")
    raw = pickle.load(f, encoding = "bytes")
    f.close()
    data = raw[1:13]
    columns = raw[0].split(", ")[1:13]

    df = {columns[i]: data[i] for i in range(12)}
    return pd.DataFrame(df)



def vincenzo2021():
    """
    Returns the V21 dataframe as a processed pandas
    object.

    Returns: pd.Dataframe
    Columns: 
        [x/y]: these are all bracket notation chemical abundances
        apogee_id: 
        age: calculated age of star in Gyr
        high_alpha
    """

    raw = vincenzo2021_raw()

    data = pd.DataFrame({"apogee_id": raw["apogee_id"]})

    data["[mg/fe]"] = raw["MgFe_stars_bracket"]
    data["[fe/h]"] = raw["FeH_stars_bracket"]

    # these are uncorrected
    data["[c/fe]_apo"] = raw["CFe_stars_bracket"]
    data["[n/fe]_apo"] = raw["NFe_stars_bracket"]

    data["[c/h]"] = raw["CHbirth_stars_bracket"]
    data["[n/h]"] = raw["NHbirth_stars_bracket"]

    data["[n/o]"] = gcem.log_to_brak(raw["NObirth_stars"], "n", "o")
    data["[c/n]"] = gcem.log_to_brak(raw["CNbirth_stars"], "c", "n")

    data["age"] = raw["age_stars"]

    # additional columns for sanity's sake
    data["[mg/h]"] = data["[mg/fe]"] + data["[fe/h]"]
    data["[o/h]"] = data["[n/h]"] - data["[n/o]"]

    data["[c/o]"] = data["[c/h]"] - data["[o/h]"]

    data["[c/mg]"] = data["[c/h]"] - data["[mg/h]"]
    data["[n/mg]"] = data["[n/h]"] - data["[mg/h]"]
    data["[o/fe]"] = data["[o/h]"] - data["[fe/h]"]

    data["high_alpha"]  = gcem.is_high_alpha(data["[mg/fe]"], data["[fe/h]"])

    # broadly filter out the chaos
    filt = data["[o/h]"] >= -10
    filt &= data["[o/h]"] <= 10
    filt &= data["[n/o]"] >= -10
    filt &= data["[n/o]"] <= 10

    return data[filt]




