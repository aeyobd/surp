import numpy as np
import pickle
import matplotlib.pyplot as plt
import vice
import pandas as pd

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

def vincenzo2021():
    f = open("CNOdredgeup.obj", "rb")
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
        "[c/n]": cn,
        "[o/h]": oh,
        "[n/o]": no
    })
    filt = data["[o/h]"] >= -10
    filt &= data["[o/h]"] <= 10
    filt &= data["[n/o]"] >= -10
    filt &= data["[n/o]"] <= 10
    
    data["[c/o]"] = data["[c/h]"] - data["[o/h]"]
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


def plot_apogee_cooh(**kwargs):
    v21 = v21 = vincenzo2021()
    plt.scatter(v21["[o/h]"], v21["[c/o]"], s=1, alpha=0.2, **kwargs)

def plot_apogee_cnfe(**kwargs):
    v21 = v21 = vincenzo2021()
    plt.scatter(v21["[fe/h]"], v21["[c/n]"], s=1, alpha=0.2, **kwargs)

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

