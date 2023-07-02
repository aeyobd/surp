import numpy as np
import pickle
import matplotlib.pyplot as plt
import vice
import pandas as pd
import seaborn as sns
from astropy.io import fits
import astropy.coordinates as coord
import astropy.units as u
import os
import requests
import sys


from .gce_math import *


def retrieve_apogee():
    """
    Checks if the apogee file exists, downloads it if not, and then returns the
    file's data"""

    script_dir = os.path.dirname(__file__)
    rel_path = "../../data/allStar-dr17-synspec_rev1.fits.1"
    abs_path = os.path.join(script_dir, rel_path)

    if not os.path.exists(abs_path):
        ans = input("Requires Apogee allStar file, download now (4GB)? Y/n")
        if ans != "Y":
            print("file does not exist, aborting")
            sys.exit()
        url = "https://data.sdss.org/sas/dr17/apogee/spectro/aspcap/dr17/synspec_rev1/allStar-dr17-synspec_rev1.fits"

        print("downloading (this may take a while)")

        file = requests.get(url, stream=True)

        i = 0
        with open(abs_path, "wb") as f:
            for chunk in file.iter_content(chunk_size=2**20):
                f.write(chunk)
                print("%i MiB / 3.7 GiB \r" % i, end="") 
                i += 1
        print("file saved!")

    ff = fits.open(abs_path, mmap=True)
    da = ff[1].data
    ff.close()

    return da


def filtered_apogee():
    da = retrieve_apogee()
    
    # read in the fits file
    
    # bit flag mask
    apogee_target2 = 1<<17 #APOGEE_MIRCLUSTER_STAR
    apogee_target2 ^= 1<<15 #APOGEE_EMISSION_STAR  emission line stars
    apogee_target2 ^= 1<<13 #APOGEE_EMBEDDEDCLUSTER_STAR embedded cluster
    
    apogee2_target3 = 1<<5 # young cluster (IN-SYNC)
    apogee2_target3 ^= 1<<18 #APOGEE2_W345
    apogee2_target3 ^= 1<<1 # EB planet
    
    mask = (da["APOGEE2_TARGET3"] & apogee2_target3) == 0
    mask &= (da["APOGEE_TARGET2"] & apogee_target2) == 0
    
    # subgiant mask
    logg = da["LOGG"]
    teff = da["TEFF"]

    mask &= logg >= 3.5
    mask &= logg <= 0.004*teff - 15.7
    mask &= logg <= 0.00070588*teff + 0.358836
    mask &= logg <= -0.0015 * teff + 12.05
    mask &= logg >= 0.0012*teff - 2.8
    
    filtered = da[mask]
    return pd.DataFrame(filtered.tolist(), columns = [c.name for c in filtered.columns])


def find_subgiants():
    """
    This returns a pd.dataframe of 
    a subgiant sample of APOGEE c.o. Jack Roberts
    
    """
    df = filtered_apogee()
    
    c = coord.SkyCoord(ra = np.array(df["RA"]) * u.deg,
                       dec = np.array(df["DEC"]) * u.deg,
                       distance = np.array(df["GAIAEDR3_R_MED_GEO"]) * u.pc,
                       frame="icrs")

    gc_c = c.transform_to(coord.Galactocentric)
    df["R_gal"] = np.array(np.sqrt(gc_c.x**2 + gc_c.y**2) / 1e3)
    df["th_gal"] = np.array(np.arctan(gc_c.y/gc_c.x))
    df["abs_z"] = np.array(np.abs(gc_c.z) / 1e3)
    df["z"] = np.array(gc_c.z / 1e3)
    
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
    rel_path = "../../data/subgiants.csv"
    abs_path = os.path.join(script_dir, rel_path)

    if not os.path.exists(abs_path):
        subgiants = find_subgiants()
        subgiants.to_csv(abs_path)
    else:
        subgiants = pd.read_csv(abs_path, index_col=0, dtype={"MEMBER": str})

    return subgiants


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
    rel_path = "../../data/CNOdredgeup.obj"
    abs_path = os.path.join(script_dir, rel_path)
    f = open(abs_path, "rb")
    raw = pickle.load(f, encoding = "bytes")
    f.close()
    data = raw[1:13]
    columns = raw[0].split(", ")[1:13]

    df = {columns[i]: data[i] for i in range(12)}
    return pd.DataFrame(df, dtype=float)



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

    data["[n/o]"] = log_to_bracket(raw["NObirth_stars"], "n", "o")
    data["[c/n]"] = log_to_bracket(raw["CNbirth_stars"], "c", "n")

    data["age"] = raw["age_stars"]

    # additional columns for sanity's sake
    data["[mg/h]"] = data["[mg/fe]"] + data["[fe/h]"]
    data["[o/h]"] = data["[n/h]"] - data["[n/o]"]

    data["[c/o]"] = data["[c/h]"] - data["[o/h]"]

    data["[c/mg]"] = data["[c/h]"] - data["[mg/h]"]
    data["[n/mg]"] = data["[n/h]"] - data["[mg/h]"]
    data["[o/fe]"] = data["[o/h]"] - data["[fe/h]"]

    high_alpha = data["[mg/fe]"] > mg_fe_cutoff(data["[fe/h]"])
    data["high_alpha"]  = high_alpha

    # broadly filter out the chaos
    filt = data["[o/h]"] >= -10
    filt &= data["[o/h]"] <= 10
    filt &= data["[n/o]"] >= -10
    filt &= data["[n/o]"] <= 10
    data["age"].replace(-999, np.NaN, inplace=True)

    return data[filt]




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

def plot_stars(x, y, ax=None, exclude_high_alpha=True, c="black", s=1,**kwargs):
    v21 = subgiants
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    if ax is None:
        ax = plt.gca()
    x = convert_name(x)
    y = convert_name(y)
    ax.scatter(v21[x], v21[y], s=s, c=c, **kwargs)#, label="V+21")

def plot_contour(x, y, ax=None, bins=50, color="black", exclude_high_alpha=True,  **kwargs):
    v21 = subgiants
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    if ax is None:
        ax = plt.gca()
    x = convert_name(x)
    y = convert_name(y)

    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    sns.kdeplot(v21, x=x, y=y, color=color, linewidths=1, **kwargs)

def plot_cooh():
    df = subgiants
    filt = ~df["high_alpha"]
    df = df[filt]
    plt.scatter(df["MG_H"], df["C_MG"], color="k", s=1, alpha=0.1)

def plot_coofe(c=-0.1, w=0.05, s=1, alpha=0.1, color="black", **kwargs):
    v21 = subgiants

    filt = v21["MG_H"] > c - w
    filt &= v21["MG_H"] < c + w
    df=  v21[filt]
    plt.scatter(df["MG_FE"], df["C_MG"], color=color, s=s, alpha=alpha, **kwargs)

def plot_mean_coofe(c=-0.1, w=0.05, s=1, color="black", **kwargs):
    v21 = subgiants

    filt = v21["MG_H"] > c - w
    filt &= v21["MG_H"] < c + w
    df=  v21[filt]
    pluto.plot_mean_track(df["MG_FE"], df["C_MG"], color="black", **kwargs)

def plot_cofeo(c=-0.1, w=0.05, s=1, alpha=0.1, **kwargs):
    v21 = subgiants

    filt = v21["MG_H"] > c - w
    filt &= v21["MG_H"] < c + w
    df=  v21[filt]
    plt.scatter(-df["MG_FE"], df["C_MG"], color="black", s=s, alpha=alpha, **kwargs)

def plot_coofe_contour(c=-0.1, w=0.05):
    v21 = subgiants

    filt = v21["MG_H"] > c - w
    filt &= v21["MG_H"] < c + w
    df=  v21[filt]
    sns.kdeplot(df, x="MG_FE", y="C_MG", color="black", linewidths=1)



def plot_v21(x, y, ax=None, exclude_high_alpha=True, s=1,**kwargs):
    v21 = vincenzo2021()
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    if ax is None:
        ax = plt.gca()
    ax.scatter(v21[x], v21[y], s=s, c="black", **kwargs)#, label="V+21")

def plot_v21_contour(x, y, bins=50,exclude_high_alpha=True,  **kwargs):
    v21 = vincenzo2021()
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    sns.kdeplot(v21, x=x, y=y, color="black", linewidths=1, **kwargs)#, label="V+21")

def plot_v21_coofe(c=-0.1, w=0.05):
    v21 = vincenzo2021()

    filt = v21["[o/h]"] > c - w
    filt &= v21["[o/h]"] < c + w
    df = v21[filt]
    df["[o/fe]"] = df["[o/h]"] - df["[fe/h]"]
    sns.kdeplot(df, x="[o/fe]", y="[c/o]", color="black", linewidths=1)

def plot_v21_cofeo(c=-0.1, w=0.05):
    v21 = vincenzo2021()

    filt = v21["[o/h]"] > c - w
    filt &= v21["[o/h]"] < c + w
    df = v21[filt]
    df["[o/fe]"] = df["[o/h]"] - df["[fe/h]"]
    df["[fe/o]"] = -df["[o/fe]"]
    sns.kdeplot(df["[fe/o]"], df["[c/o]"], color="black", linewidths=1)

def plot_v21_coofe_scatter(c=-0.1, w=0.05):
    v21 = vincenzo2021()

    filt = v21["[o/h]"] > c - w
    filt &= v21["[o/h]"] < c + w
    df=  v21[filt]
    df["[o/fe]"] = df["[o/h]"] - df["[fe/h]"]
    df["[fe/o]"] = -df["[o/fe]"]
    plt.scatter(df["[o/fe]"], df["[c/o]"], color="black", s=1)

def plot_v21_cofeo_scatter(c=-0.1, w=0.05):
    v21 = vincenzo2021()

    filt = v21["[o/h]"] > c - w
    filt &= v21["[o/h]"] < c + w
    df=  v21[filt]
    df["[o/fe]"] = df["[o/h]"] - df["[fe/h]"]
    df["[fe/o]"] = -df["[o/fe]"]
    plt.scatter(df["[fe/o]"], df["[c/o]"], color="black", s=1)

def calc_mean(x, y, bins=50, xlim=None):
    if type(bins) is int:
        if xlim is None:
            xlim = (min(x), max(x))
        bins = np.linspace(xlim[0], xlim[1], 50)

    N = len(bins) - 1
    means = np.zeros(N)
    sds = np.zeros(N)
    counts = np.zeros(N)

    for i in range(N):
        filt = y[(x >= bins[i]) & (x < bins[i+1])]
        means[i] = np.mean(filt)
        sds[i] = np.std(filt)
        counts[i] = len(filt)

    return bins, means, sds, counts

def calc_mean_v21(x, y, bins=50, xlim=None, exclude_high_alpha=True):
    v21 = vincenzo2021()
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]

    if type(bins) is int:
        if xlim is None:
            xlim = (min(v21[x]), max(v21[x]))
        bins = np.linspace(xlim[0], xlim[1], 50)

    N = len(bins) - 1
    means = np.zeros(N)
    sds = np.zeros(N)
    counts = np.zeros(N)

    for i in range(N):
        filt = v21[(v21[x] >= bins[i]) & (v21[x] < bins[i+1])]
        means[i] = np.mean(filt[y])
        sds[i] = np.std(filt[y])
        counts[i] = len(filt)

    return bins, means, sds, counts

def plot_mean_v21(x, y, ax=None, bins=50, exclude_high_alpha=True, xlim=None, ylim=None, **kwargs):
    if ax is None:
        ax = plt.gca()

    bins, means, sds, counts = calc_mean_v21(x, y, bins, xlim, exclude_high_alpha)

    ax.plot(bins[:-1], means, label="V21", color="black")
    # ax.fill_between(bins[:-1], means-sds, means+sds, color="black", label="V+21")

    return means, sds
    # ax.plot(bins[:-1], means-sds, color="black", ls=":")
    # ax.plot(bins[:-1], means+sds, color="black", ls=":")


    

def plot_skillman20_cooh(**kwargs):
    c_o = [-0.04, -0.08, -0.31, -0.39,-.28,-.34,-.30,-.25,-.63,-.47]
    c_o_err = [.07,.04,.12,.19,.12,.11,.09,.17,.50,.46]
    o_h = [8.57,8.57,8.48,8.45,8.43,8.39,8.42,8.35,8.26,8.14]
    o_h_err = [0.02,0.01,.02,.05,.01,.02,.01,.01,.03,.03]
    plt.errorbar(log_to_bracket(o_h, "o") - 12, log_to_bracket(c_o, "c", "o"), yerr=c_o_err, xerr = o_h_err, fmt="o", **kwargs)

def plot_skillman20_cnoh(**kwargs):
    o_h = [8.57,8.57,8.48,8.45,8.43,8.39,8.42,8.35,8.26,8.14]
    o_h_err = [0.02,0.01,.02,.05,.01,.02,.01,.01,.03,.03]
    c_n = [.92,.93,.69,.81,.90,.81,.83,.88,.70,.90]
    c_n_err = [.08,.05,.13,.21,.13,.13,.10,.18,.50,.50]
    plt.errorbar(log_to_bracket(o_h, "o") - 12, log_to_bracket(c_n, "c", "n"), yerr=c_n_err, xerr = o_h_err, fmt="o", **kwargs)




subgiants = read_subgiants()
