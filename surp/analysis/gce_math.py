import numpy as np
import vice


from .._globals import Z_SUN

def Z_to_MH(Z):
    if type(Z) in (list, tuple):
        x = np.array(Z)
    else:
        x = Z
    return np.log10(x/Z_SUN)

def MH_to_Z(M_H):
    if type(M_H) in (list, tuple):
        x = np.array(M_H)
    else:
        x = M_H
    return Z_SUN * 10**x


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


def bracket_to_abundance(data, ele, ele2="h"):
    if ele2 == "h":
        return 10**data * vice.solar_z(ele)
    else:
        return 10**data * vice.solar_z(ele) / vice.solar_z(ele2)


def A_to_Z(A, ele, mixing_correction=0, X=0.71):
    logZ = (A - 12)  + np.log10(X * mm_of_elements[ele]) 
    return 10**(logZ + mixing_correction)

def abundance_to_bracket(data, ele, ele2="h"):
    if ele2.lower() == "h":
        return np.log10(data/vice.solar_z(ele))
    else:
        return np.log10(data) - np.log10(vice.solar_z(ele) / vice.solar_z(ele2))


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


def is_high_alpha(mg_fe, fe_h):
    return mg_fe > mg_fe_cutoff(fe_h)

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
