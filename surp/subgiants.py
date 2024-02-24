import os
import numpy as np
import pandas as pd

from .gce_math import *
from .utils import download_or_load


def bracket(df, ele, ele2="H"):
    """
    Helper function for subgiants()
    creates the abundance ratio [A/B]
    from the  APOGEE dataframe
    """
    if ele2 == "H":
        if ele == "FE":
            return df["FE_H"]
        else:
            return df["%s_FE" % ele] + df["FE_H"]
    else:
        if ele2 == "FE":
            return df["%s_FE" % ele]
        else:
            return df["%s_FE" % ele] - df["%s_FE" % ele2]


def retrieve_apogee():
    """
    Checks if the apogee file exists, downloads it if not, and then returns the
    file's data"""

    rel_path = "../data/allStar-dr17-synspec_rev1.fits.1"
    url = "https://data.sdss.org/sas/dr17/apogee/spectro/aspcap/dr17/synspec_rev1/allStar-dr17-synspec_rev1.fits"

    return download_or_load(rel_path, url, "3.7")


def retrieve_astroNN():
    rel_path = "../data/apogee_astroNN-DR17.fits"
    url = "https://data.sdss.org/sas/dr17/env/APOGEE_ASTRO_NN/apogee_astroNN-DR17.fits"
    
    return download_or_load(rel_path, url, "0.7").to_pandas()
    
    
def filtered_apogee():
    da = retrieve_apogee()
    
    # bit flag mask
    apogee_target2 = 1<<17 #APOGEE_MIRCLUSTER_STAR
    apogee_target2 ^= 1<<15 #APOGEE_EMISSION_STAR  emission line stars
    apogee_target2 ^= 1<<13 #APOGEE_EMBEDDEDCLUSTER_STAR embedded cluster
    
    apogee2_target3 = 1<<5 # young cluster (IN-SYNC)
    apogee2_target3 ^= 1<<18 #APOGEE2_W345
    apogee2_target3 ^= 1<<1 # EB planet

    apogee_aspcapflag = 1<<23 # starbad
    apogee_aspcapflag ^= 1<<31 # no_aspcap_result

    
    mask = (da["APOGEE2_TARGET3"] & apogee2_target3) == 0
    mask &= (da["APOGEE_TARGET2"] & apogee_target2) == 0
    mask &= (da["ASPCAPFLAG"] & apogee_aspcapflag) == 0
    
    # subgiant mask
    logg = da["LOGG"]
    teff = da["TEFF"]

    mask &= logg >= 3.5
    mask &= logg <= 0.004*teff - 15.7
    mask &= logg <= 0.00070588*teff + 0.358836
    mask &= logg <= -0.0015 * teff + 12.05
    mask &= logg >= 0.0012*teff - 2.8
    
    filtered = da[mask]
    df =  filtered.to_pandas()
    return df[~df.APOGEE_ID.duplicated(keep="first")]


def convert_strings(df):
    str_df = df.select_dtypes([np.byte])
    for col in str_df:
        df[col] = [a.decode() for a in df[col]]
    return df

def find_subgiants():
    """
    This returns a pd.dataframe of 
    a subgiant sample of APOGEE c.o. Jack Roberts
    
    """
    df_a = filtered_apogee()
    
    astroNN = retrieve_astroNN()

    df_aNN = astroNN[~astroNN.APOGEE_ID.duplicated(keep="first")].copy()
    df_aNN.set_index("APOGEE_ID", inplace=True)
    df = df_a.set_index("APOGEE_ID").join(df_aNN, rsuffix="_ANN").copy()
    df["R_gal"] = df.galr
    df["z_gal"] = df.galz

    df["abs_z"] = np.abs(df.z_gal)
    
    # Add useful abundance ratios
    df["O_H"] = bracket(df, "O")
    df["MG_H"] = bracket(df, "MG")
    df["C_O"] = bracket(df, "C", "O")
    df["C_MG"] = bracket(df, "C", "MG")
    df["C_H"] = bracket(df, "C", "H")

    df["C_N"] = bracket(df, "C", "N")
    df["N_H"] = bracket(df, "N", "H")
    df["N_O"] = bracket(df, "N", "O")
    df["N_MG"] = bracket(df, "N", "MG")

    df["FE_O"] = -df["O_FE"]
    df["FE_MG"] = -df["MG_FE"]

    df["C_MG_ERR"] = df["C_FE_ERR"] + df["MG_FE_ERR"]
    df["N_MG_ERR"] = df["N_FE_ERR"] + df["MG_FE_ERR"]
    df["C_N_ERR"] = df["N_FE_ERR"] + df["C_FE_ERR"]
    
    # add high/low alpha column
    df["high_alpha"] = df["MG_FE"] > mg_fe_cutoff(df["FE_H"])
    
    # df.drop(columns=["X_M_SPEC", "X_H_SPEC"], inplace=True)
    return df


def read_subgiants():
    """
    Either reads in the subgiants from a csv file or
    calculates the subgiant sample from apogee and writes this to 
    a file if the file does not yet exist
    """
    script_dir = os.path.dirname(__file__)
    rel_path = "../data/subgiants.csv"
    abs_path = os.path.join(script_dir, rel_path)

    if not os.path.exists(abs_path):
        subgiants = find_subgiants()
        subgiants.to_csv(abs_path)
    else:
        subgiants = pd.read_csv(abs_path, index_col=0, dtype={"MEMBER": str})

    return subgiants



def convert_name(x):
    """
    Helper function. Converts a name like
    [a/b] to A_B
    """
    s = x.upper()
    s = s.replace("[", "")
    s = s.replace("]", "")
    s = s.replace("/", "_")

    return s

