import numpy as np
import vice
import molmass

from ._globals import Z_SUN
from .utils import arg_numpylike


@arg_numpylike()
def Z_to_MH(Z):
    return np.log10(Z/Z_SUN)

@arg_numpylike()
def MH_to_Z(M_H):
    return Z_SUN * 10**M_H


@arg_numpylike()
def log_to_brak(ratio, elem, elem2="H"):
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
        
    if elem2 == "H":
        return ratio - np.log10(vice.solar_z(elem)) + np.log10(molar_mass(elem))
    else:
        return ratio - np.log10(vice.solar_z(elem)/vice.solar_z(elem2)) + np.log10(molar_mass(elem)/molar_mass(elem2))


@arg_numpylike()
def eps_to_brak(eps, ele):
    return log_to_brak(eps, ele) - 12


@arg_numpylike()
def brak_to_abund(data, ele, ele2="h"):
    if ele2 == "h":
        return 10**data * vice.solar_z(ele)
    else:
        return 10**data * vice.solar_z(ele) / vice.solar_z(ele2)

def molar_mass(ele):
    return molmass.ELEMENTS[ele.upper()].mass

def A_to_Z(A, ele, mixing_correction=0, X=0.71):
    logZ = (A - 12)  + np.log10(X * mmass(ele)) 
    return 10**(logZ + mixing_correction)

@arg_numpylike()
def abund_to_brak(data, ele, ele2="h"):
    if ele2.lower() == "h":
        return np.log10(data/vice.solar_z(ele))
    else:
        return np.log10(data) - np.log10(vice.solar_z(ele) / vice.solar_z(ele2))


@arg_numpylike()
@arg_numpylike(1)
def cpn(c1, n1):
    return np.log10( (brak_to_abund(c, "c") + brak_to_abund(n, "n")) / (vice.solar_z("c") + vice.solar_z("n")) )


@arg_numpylike()
@arg_numpylike(1)
def cmn(c1, n1):
    return np.log10( (brak_to_abund(c, "c") - brak_to_abund(n, "n")) / (vice.solar_z("c") - vice.solar_z("n")) )




@arg_numpylike()
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


@arg_numpylike()
@arg_numpylike(1)
def is_high_alpha(mg_fe, fe_h):
    return np.where(mg_fe > mg_fe_cutoff(fe_h), True, False)



