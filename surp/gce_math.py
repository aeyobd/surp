import numpy as np
import vice # used for solar_z
import molmass # used for molar_mass

from ._globals import Z_SUN, X_SUN, Y_SUN
from .utils import arg_numpylike

"""
some brief notes

- Z represents the mass fraction of an element
- log represents the log of the number fraction of an element
- eps represents 12 + log

Note that there are different functions for absolute and relative abundances
because these represent different things.
"""




def solar_z(ele):
    """Solar abundance scale. Overloaded from VICE.
    Adds convenience definitions solar_z("H") = X_SUN and solar_z("M") = Z_SUN
    """
    if ele.lower() == "h":
        return X_SUN
    elif ele.lower() == "he":
        return Y_SUN
    elif ele.upper() == "M":
        return Z_SUN
    else:
        return vice.solar_z(ele)


@np.vectorize
def molar_mass(ele):
    """Returns the molar mass of an element (or array of elements).
    """
    return molmass.ELEMENTS[ele.title()].mass
    

@arg_numpylike()
def Z_to_MH(Z):
    """Converts the mass fraction to the scaled solar log"""
    return np.log10(Z/Z_SUN)


@arg_numpylike()
def MH_to_Z(M_H):
    return Z_SUN * 10**M_H





""" Converts a bracket notation [A/B] into mass abundance ratio Z_A/Z_B.
"""
@arg_numpylike()
def brak_to_abund_ratio(data, ele, ele2):
    return 10.0**data * solar_z(ele) / solar_z(ele2)


""" Converts a bracket notation [A/H] into mass abundance Z_A."""
@arg_numpylike()
def brak_to_abund(data, ele):
    return 10.0**data * solar_z(ele)


""" Converts a mass abundance A/B into bracket notation [A/B].
If ele2 == H, then the input is instead Z_A
"""
@arg_numpylike()
def abund_ratio_to_brak(data, ele, ele2):
    return np.log10(data) - np.log10(solar_z(ele) / solar_z(ele2))


""" Converts a mass abundance Z_A into bracket notation [A/H]."""
@arg_numpylike()
def abund_to_brak(data, ele):
    return np.log10(data) - np.log10(solar_z(ele))



@arg_numpylike()
def log_to_brak(ratio, elem, elem2="H"):
    """Calculates log A/B to A/B
    """
        
    return ratio - np.log10(solar_z(elem)/solar_z(elem2)) + np.log10(molar_mass(elem)/molar_mass(elem2))




@arg_numpylike()
def log_to_abundance_ratio(ratio, ele, ele2="H"):
    ratio = np.float64(ratio)
    return 10**ratio * molar_mass(ele) / molar_mass(ele2)


@arg_numpylike()
def log_to_abundance(ratio, ele):
    ratio = np.float64(ratio)
    return 10**ratio * molar_mass(ele) * X_SUN / molar_mass("h")


@arg_numpylike()
def eps_to_log(eps):
    return eps - 12


@arg_numpylike()
def eps_to_brak(eps, ele):
    return eps_to_log(log_to_brak(eps, ele))


@arg_numpylike()
def eps_to_abundance(eps, ele):
    return log_to_abundance(eps_to_log(eps), ele)





""" C + N given [C/H] and [N/H]"""
@arg_numpylike()
@arg_numpylike(1)
def cpn(c, n):
    return np.log10( (brak_to_abund(c, "c") + brak_to_abund(n, "n")) / (solar_z("c") + solar_z("n")) )



""" [C - N/H] given [C/H] and [N/H]"""
@arg_numpylike()
@arg_numpylike(1)
def cmn(c, n):
    return np.log10( (brak_to_abund(c, "c") - brak_to_abund(n, "n")) / (solar_z("c") - solar_z("n")) )




@arg_numpylike()
def mg_fe_cutoff(fe_h):
    """
    The cutoff between the high and low alpha seqeunces

    described by
    [Mg/Fe] = 0.16 - 0.13*[Fe/H] for [Fe/H] < 0
    [Mg/Fe] = 0.16 for [Fe/H] >= 0

    Is as used in Roberts et al. 2024 which is a +0.04 dex correction on
    Weinberg et al. (2019).

    Parameters
    ----------
    fe_h: float or np.array
        The [Fe/H] values to evaluate the boandry at

    Returns
    -------
    mg_fe: float or np.array
        The [Mg/Fe] above which the high alpha sequence is defined
    """
    return 0.16 - (fe_h < 0) * 0.13 * fe_h



"""Returns True if the star is in the high alpha sequence"""
@arg_numpylike()
@arg_numpylike(1)
def is_high_alpha(mg_fe, fe_h):
    return np.where(mg_fe > mg_fe_cutoff(fe_h), True, False)



