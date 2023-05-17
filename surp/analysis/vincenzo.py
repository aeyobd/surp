import numpy as np
import pickle
import matplotlib.pyplot as plt
import vice
import pandas as pd
import os


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
    rel_path = "./CNOdredgeup.obj"
    abs_path = os.path.join(script_dir, rel_path)
    f = open(abs_path, "rb")
    raw = pickle.load(f, encoding = "bytes")
    f.close()
    data = raw[1:13]
    columns = raw[0].split(", ")[1:13]

    df = {columns[i]: data[i] for i in range(12)}
    return pd.DataFrame(df, dtype=float)

def mg_fe_cutoff(fe_h):
    """
    The cutoff between the high and low alpha seqeunces

    Parameters
    ----------
    fe_h: float or np.array
        The [Fe/H] values to evaluate the boandry at

    Returns
    -------
    mg_fe: float or np.array
        The [Mg/Fe] above which the high alpha sequence is defined
    """
    return 0.12 - (fe_h < 0) * 0.13 * fe_h


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


def log_to_bracket(ratio, elem, elem2="H"):
    """Calculates [A/B] from log A/B
    Parameters
    ----------
    ratio : float or list-like
        The input value of log A/B
    elem : str
        The string of element A
    elem2 : str
        The string of element B, default H
        
    Returns
    -------
    The value of [A/B]
    """

    if isinstance(ratio, list):
        r = np.array(ratio)
    else:
        r = ratio
        

    if elem2 == "H":
        return r - np.log10(vice.solar_z(elem)) + np.log10(mm_of_elements[elem])
    else:
        return r - np.log10(vice.solar_z(elem)/vice.solar_z(elem2)) + np.log10(mm_of_elements[elem]/mm_of_elements[elem2])




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


def bracket_to_abundance(data, ele, ele2="h"):
    if ele2 == "h":
        return 10**data * vice.solar_z(ele)
    else:
        return 10**data * vice.solar_z(ele) / vice.solar_z(ele2)

def abundance_to_bracket(data, ele):
    return np.log10(data/vice.solar_z(ele))


mm_of_elements = {'h': 1.00794, 'he': 4.002602, 'li': 6.941, 'be': 9.012182,
                  'b': 10.811, 'c': 12.0107, 'n': 14.0067, 'o': 15.9994, 
                  'f': 18.9984032, 'ne': 20.1797, 'na': 22.98976928, 'mg': 24.305, 
                  'al': 26.9815386, 'si': 28.0855, 'p': 30.973762, 's': 32.065, 
                  'cl': 35.453, 'ar': 39.948, 'k': 39.0983, 'ca': 40.078,
                  'sc': 44.955912, 'ti': 47.867, 'v': 50.9415, 'cr': 51.9961, 
                  'mn': 54.938045, 'fe': 55.845, 'co': 58.933195, 'ni': 58.6934, 
                  'cu': 63.546, 'zn': 65.409, 'ga': 69.723, 'ge': 72.64,
                  'as': 74.9216, 'se': 78.96, 'br': 79.904, 'kr': 83.798, 
                  'rb': 85.4678, 'sr': 87.62, 'y': 88.90585, 'zr': 91.224, 
                  'nb': 92.90638, 'mo': 95.94, 'tc': 98.9063, 'ru': 101.07, 
                  'rh': 102.9055, 'pd': 106.42, 'ag': 107.8682, 'cd': 112.411, 
                  'in': 114.818, 'sn': 118.71, 'sb': 121.760, 'te': 127.6,
                  'i': 126.90447, 'xe': 131.293, 'cs': 132.9054519, 'ba': 137.327, 
                  'la': 138.90547, 'ce': 140.116, 'pr': 140.90465, 'nd': 144.242,
                  'pm': 146.9151, 'sm': 150.36, 'eu': 151.964, 'gd': 157.25,
                  'tb': 158.92535, 'dy': 162.5, 'ho': 164.93032, 'er': 167.259,
                  'tm': 168.93421, 'yb': 173.04, 'lu': 174.967, 'hf': 178.49,
                  'ta': 180.9479, 'w': 183.84, 're': 186.207, 'os': 190.23,
                  'ir': 192.217, 'pt': 195.084, 'au': 196.966569, 'hg': 200.59,
                  'tl': 204.3833, 'pb': 207.2, 'bi': 208.9804, 'po': 208.9824,
                  'at': 209.9871, 'rn': 222.0176, 'fr': 223.0197, 'ra': 226.0254, 
                  'ac': 227.0278, 'th': 232.03806, 'pa': 231.03588, 'u': 238.02891,
                  'np': 237.0482, 'pu': 244.0642, 'am': 243.0614, 'cm': 247.0703,
                  'bk': 247.0703, 'cf': 251.0796, 'es': 252.0829, 'fm': 257.0951,
                  'md': 258.0951, 'no': 259.1009, 'lr': 262, 'rf': 267,
                  'db': 268, 'sg': 271, 'bh': 270, 'hs': 269, 'mt': 278,
                  'ds': 281, 'rg': 281, 'cn': 285, 'nh': 284, 
                  'fl': 289, 'mc': 289, 'lv': 292, 'ts': 294, 
                  'og': 294,
                  '': 0}

subgiants = find_subgiants()
