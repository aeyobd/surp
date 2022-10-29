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

mm_of_elements = {'h': 1.00794, 'he': 4.002602, 'li': 6.941, 'be': 9.012182, 'b': 10.811, 'c': 12.0107, 'n': 14.0067,
                  'o': 15.9994, 'f': 18.9984032, 'ne': 20.1797, 'na': 22.98976928, 'mg': 24.305, 'al': 26.9815386,
                  'si': 28.0855, 'p': 30.973762, 's': 32.065, 'cl': 35.453, 'ar': 39.948, 'k': 39.0983, 'ca': 40.078,
                  'sc': 44.955912, 'ti': 47.867, 'v': 50.9415, 'cr': 51.9961, 'mn': 54.938045,
                  'fe': 55.845, 'co': 58.933195, 'ni': 58.6934, 'cu': 63.546, 'zn': 65.409, 'ga': 69.723, 'ge': 72.64,
                  'as': 74.9216, 'se': 78.96, 'br': 79.904, 'kr': 83.798, 'rb': 85.4678, 'sr': 87.62, 'y': 88.90585,
                  'zr': 91.224, 'nb': 92.90638, 'mo': 95.94, 'tc': 98.9063, 'ru': 101.07, 'rh': 102.9055, 'pd': 106.42,
                  'ag': 107.8682, 'cd': 112.411, 'in': 114.818, 'sn': 118.71, 'sb': 121.760, 'te': 127.6,
                  'i': 126.90447, 'xe': 131.293, 'cs': 132.9054519, 'ba': 137.327, 'la': 138.90547, 'ce': 140.116,
                  'pr': 140.90465, 'nd': 144.242, 'pm': 146.9151, 'sm': 150.36, 'eu': 151.964, 'gd': 157.25,
                  'tb': 158.92535, 'dy': 162.5, 'ho': 164.93032, 'er': 167.259, 'tm': 168.93421, 'yb': 173.04,
                  'lu': 174.967, 'hf': 178.49, 'ta': 180.9479, 'w': 183.84, 're': 186.207, 'os': 190.23, 'ir': 192.217,
                  'pt': 195.084, 'au': 196.966569, 'hg': 200.59, 'tl': 204.3833, 'pb': 207.2, 'bi': 208.9804,
                  'po': 208.9824, 'at': 209.9871, 'rn': 222.0176, 'fr': 223.0197, 'ra': 226.0254, 'ac': 227.0278,
                  'th': 232.03806, 'pa': 231.03588, 'u': 238.02891, 'np': 237.0482, 'pu': 244.0642, 'am': 243.0614,
                  'cm': 247.0703, 'bk': 247.0703, 'cf': 251.0796, 'es': 252.0829, 'fm': 257.0951, 'md': 258.0951,
                  'no': 259.1009, 'lr': 262, 'rf': 267, 'db': 268, 'sg': 271, 'bh': 270, 'hs': 269, 'mt': 278,
                  'ds': 281, 'rg': 281, 'cn': 285, 'nh': 284, 'fl': 289, 'mc': 289, 'lv': 292, 'ts': 294, 'og': 294,
                  '': 0}

def logNO_bracket_conversion(logNO):
    return np.log10(14.006/15.999) + logNO - np.log10(vice.solar_z["n"]/vice.solar_z["o"])

def find_subgiants():
    """
    This returns a pd.dataframe of 
    a subgiant sample of APOGEE c.o. Jack Roberts
    
    """
    
    # read in the fits file
    script_dir = os.path.dirname(__file__)
    rel_path = "../data/allStar-dr17-synspec_rev1.fits.1"
    abs_path = os.path.join(script_dir, rel_path)
    ff = fits.open(abs_path, mmap=True)
    da = ff[1].data
    ff.close()
    
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
    df = pd.DataFrame(filtered.tolist(), columns = [c.name for c in filtered.columns])
    
    # calculate galacteocentric coordinates (not super useful but here for fun)
    c = coord.SkyCoord(ra = df["RA"] * u.degree,
                               dec = df["DEC"] * u.degree,
                               distance = df["GAIAEDR3_R_MED_GEO"] * u.pc,
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
    
    # add high/low alpha column
    def mg_fe_fe_h_cutoff(fe_h):
        return 0.12 - 0.13*fe_h *(fe_h < 0)

    df["high_alpha"] = df["MG_FE"] > mg_fe_fe_h_cutoff(df["FE_H"])
    
    return df


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


def vincenzo2021():
    script_dir = os.path.dirname(__file__)
    rel_path = "../data/CNOdredgeup.obj"
    abs_path = os.path.join(script_dir, rel_path)
    f = open(abs_path, "rb")
    raw = pickle.load(f, encoding = "bytes")
    f.close()
    
    mgfe = raw[1].tolist()
    feh = raw[2].tolist()
    cfe = raw[3].tolist()
    nfe = raw[4].tolist()
    ch = raw[5].tolist()
    nh = raw[6].tolist()
    age = raw[7].tolist()
    cn = raw[9].tolist()
    no = [logNO_bracket_conversion(_) for _ in raw[11]]
    oh = [a - b for a, b in zip(nh, no)]
    data = pd.DataFrame({
        "[mg/fe]": mgfe,
        "[fe/h]": feh,
        "[c/fe]": cfe,
        "[n/fe]": nfe,
        "[c/h]": ch,
        "[n/h]": nh,
        "age": age,
        "[c/n]": log_to_bracket(cn, "c", "n"),
        "[o/h]": oh,
        "[n/o]": no
    })
    filt = data["[o/h]"] >= -10
    filt &= data["[o/h]"] <= 10
    filt &= data["[n/o]"] >= -10
    filt &= data["[n/o]"] <= 10
    
    data["[c/o]"] = data["[c/h]"] - data["[o/h]"]
    data["[c/fe]"] = data["[c/h]"] - data["[fe/h]"]


    data["[c+n/h]"] = np.log10((
        bracket_to_abundance(data["[c/h]"], "C") +
        bracket_to_abundance(data["[n/h]"], "N"))
        / (vice.solar_z("C") + vice.solar_z("N")))

    data["[c+n/o]"] = data["[c+n/h]"] - data["[o/h]"]

    data["age"].replace(-999, np.NaN, inplace=True)
    data["[o/fe]"] = data["[o/h]"] - data["[fe/h]"]

    def o_fe_cutoff(fe_h):
        return 0.12 - (fe_h < 0) * 0.13 * fe_h

    high_alpha = data["[o/fe]"] > o_fe_cutoff(data["[fe/h]"])
    data["high_alpha"]  = high_alpha

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

def plot_stars(x, y, ax=None, exclude_high_alpha=True, s=1,**kwargs):
    v21 = subgiants
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    if ax is None:
        ax = plt.gca()
    x = convert_name(x)
    y = convert_name(y)
    ax.scatter(v21[x], v21[y], s=s, c="black", **kwargs)#, label="V+21")

def plot_contour(x, y, ax=None, bins=50,exclude_high_alpha=True,  **kwargs):
    v21 = subgiants
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    if ax is None:
        ax = plt.gca()
    x = convert_name(x)
    y = convert_name(y)

    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    sns.kdeplot(v21[x], v21[y], color="black", linewidths=1, **kwargs)

def plot_cooh():
    df = subgiants
    filt = ~df["high_alpha"]
    df = df[filt]
    plt.scatter(df["MG_H"], df["C_MG"], color="k", s=1, alpha=0.1)

def plot_coofe(c=-0.1, w=0.05, s=1, alpha=0.1, **kwargs):
    v21 = subgiants

    filt = v21["MG_H"] > c - w
    filt &= v21["MG_H"] < c + w
    df=  v21[filt]
    plt.scatter(df["MG_FE"], df["C_MG"], color="black", s=s, alpha=alpha, **kwargs)

def plot_coofe_contour(c=-0.1, w=0.05):
    v21 = subgiants

    filt = v21["MG_H"] > c - w
    filt &= v21["MG_H"] < c + w
    df=  v21[filt]
    sns.kdeplot(df["MG_FE"], df["C_MG"], color="black", linewidths=1)



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
    sns.kdeplot(v21[x], v21[y], color="black", linewidths=1, **kwargs)#, label="V+21")

def plot_v21_coofe(c=-0.1, w=0.05):
    v21 = vincenzo2021()

    filt = v21["[o/h]"] > c - w
    filt &= v21["[o/h]"] < c + w
    df = v21[filt]
    df["[o/fe]"] = df["[o/h]"] - df["[fe/h]"]
    sns.kdeplot(df["[o/fe]"], df["[c/o]"], color="black", linewidths=1)

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


def bracket_to_abundance(data, ele, ele2="h"):
    if ele2 == "h":
        return 10**data * vice.solar_z(ele)
    else:
        return 10**data * vice.solar_z(ele) / vice.solar_z(ele2)

def abundance_to_bracket(data, ele):
    return np.log10(data/vice.solar_z(ele))

def cpn(c1, n1):
    if type(c1) in (list, tuple):
        c = np.array(c1)
    else:
        c = c1
    if type(n1) in (list, tuple):
        n = np.array(n1)
    else:
        n = n1

    return np.log10( (bracket_to_abundance(c, "c") + bracket_to_abundance(n, "n")) / (vice.solar_z("c") + vice.solar_z("n")) )

def cmn(c1, n1):
    if type(c1) in (list, tuple):
        c = np.array(c1)
    else:
        c = c1
    if type(n1) in (list, tuple):
        n = np.array(n1)
    else:
        n = n1
    return np.log10( (bracket_to_abundance(c, "c") - bracket_to_abundance(n, "n")) / (vice.solar_z("c") - vice.solar_z("n")) )
    

def skillman20():
    p

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


subgiants = find_subgiants()
