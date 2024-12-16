import vice
from vice.yields import ccsne, sneia, agb

from surp._globals import Z_SUN

from .utils import print_row
from .agb_interpolator import interpolator
from .yield_params import YieldParams
import numpy as np

from surp import yield_models
from surp.yield_models import ZeroAGB

import os

ELEMS = ["c", "n", "o", "mg", "fe"]



def set_magg22_scale(verbose=True):
    """Sets the solar_z values of c, o, mg, fe, and n to magg++2022
    If isotopic is true, sets isotopic c12 and c13 abundances using
    the ratio of 89.3 ± 0.2 quoted in Asplund et al. 2021 from Meija et al. 2016)
    """
    vice.solar_z["c"] = 0.00339
    vice.solar_z["o"] = 0.00733
    vice.solar_z["mg"] = 0.000671
    vice.solar_z["fe"] = 0.00137
    vice.solar_z["n"] = 0.00104
    vice.solar_z["ag"] = 1e-3 * vice.solar_z["c"]

    if verbose:
        print("yields set to Magg et al. 2022 abundances")




def set_defaults() -> None:
    """Sets the constant default yield settings used in the carbon paper"""
    sneia.settings["c"] = 0
    # ccsne.settings["c"]
    # agb.settings["c"]

    ccsne.settings["o"] = 7.13e-3
    sneia.settings["o"] = 0
    agb.settings["o"] = yield_models.ZeroAGB()

    # ccsne.settings["fe"] = 
    # sneia.settings["fe"] = 7.7e-4 
    agb.settings["fe"] = yield_models.ZeroAGB()

    ccsne.settings["mg"] = 6.52e-4
    sneia.settings["mg"] = 0
    agb.settings["mg"] = yield_models.ZeroAGB()

    #agb.settings["n"] = LinAGB(eta=5.02e-4, y0=0)
    #ccsne.settings["n"] = 5e-4
    sneia.settings["n"] = 0



def set_yields(params=None, verbose=False, **kwargs):
    """ 
    set_yields(params, verbose=False, **kwargs)
    Ses the yields and abundace scale for the C project. """

    if params is None:
        dirname = os.path.dirname(__file__)
        params = YieldParams.from_file(os.path.join(dirname, "yield_params.toml"))

    params = params.to_dict()
    params = params | kwargs
    params = YieldParams(**params)

    set_magg22_scale(verbose=verbose)
    vice.mlr.setting = params.mlr

    set_defaults()

    agb.settings["c"] = get_c_agb_model(params)
    ccsne.settings["c"] = get_c_cc_model(params)
    sneia.settings["c"] = params.y_c_ia

    agb.settings["n"] = get_n_agb_model(params)
    ccsne.settings["n"] = params.y0_n_cc

    sneia.settings["fe"] = params.y_fe_ia
    ccsne.settings["fe"] = params.y_fe_cc

    scale_yields(params.yield_scale)


    if verbose:
        print_yields()


def get_c_agb_model(params):
    """Returns an AGB model for C with properties specified in params"""
    if params.Y_c_agb == "A":
        model = yield_models.C_AGB_Model(**params.kwargs_c_agb)
    else:
        model = interpolator("c", study=params.Y_c_agb, **params.kwargs_c_agb)

    model *= params.alpha_c_agb
    return model


def get_c_cc_model(params):
    """Returns a CC model for C with properties specified in params"""
    if params.y_c_cc == "BiLin":
        model = yield_models.BiLin_CC(y0=params.y0_c_cc, zeta=params.zeta_c_cc, **params.kwargs_c_cc)
    elif params.y_c_cc == "Lin":
        model = yield_models.Lin_CC(y0=params.y0_c_cc, zeta=params.zeta_c_cc)
    elif params.y_c_cc == "LogLin":
        model = yield_models.LogLin_CC(y0=params.y0_c_cc, zeta=params.zeta_c_cc, **params.kwargs_c_cc)
    elif params.y_c_cc == "BiLogLin":
        model = yield_models.BiLogLin_CC(y0=params.y0_c_cc, zeta=params.zeta_c_cc, **params.kwargs_c_cc)
    elif params.y_c_cc == "Quadratic":
        model = yield_models.Quadratic_CC(y0=params.y0_c_cc, zeta=params.zeta_c_cc, **params.kwargs_c_cc)
    else:
        model = params.y_c_cc

    return model


def get_n_agb_model(params):
    if params.Y_n_agb == "A":
        model = yield_models.LinAGB(eta=params.eta_n_agb, y0=params.y0_n_agb)
    else:
        model = params.Y_n_agb

    return model


def scale_yields(scale=1):
    """scales the yields of all elements by a uniform factor"""
    if scale==1:
        return

    for elem in ELEMS:
        ccsne.settings[elem] = ccsne.settings[elem] * scale
        sneia.settings[elem] = sneia.settings[elem] * scale
        yagb = agb.settings[elem]
        if isinstance(yagb, interpolator):
            agb.settings[elem].prefactor *= scale
        else:
            agb.settings[elem] = agb.settings[elem] * scale


def print_yields():
    """
    Debugging function to print the current yield settings
    """
    print("Yield settings")
    widths = [8, 10, 30, 30, 30]
    print_row("X", "Z_solar", "CC", "agb", "SN Ia", widths=widths)

    # print values
    for elem in ["c", "n", "o", "mg", "fe"]:
        print_row(elem, 
                vice.solar_z(elem),
                ccsne.settings[elem],
                agb.settings[elem],
                sneia.settings[elem],
                  widths=widths
                  )

    print()
    print()



"""
Calculates the current yield at a given metallicity using VICEs 
SSP function (i.e. at 10 Gyr)

Parameters
----------
Z : float
    The metallicity at which to calculate the yield
ele : str [default="c"]
    The element for which to calculate the yield
kind : str [default="all"]
    The kind of yield to calculate. Options are "all", "cc", "ia" or "agb" for alll yields, cc yields, ia yields, or agb yields respectively.

"""
def calc_y(Z=Z_SUN, ele="c", kind="all", t_end=10):
    if hasattr(Z, "__len__"):
        y = np.array( [_calc_y_of_kind(z, ele, kind, t_end=t_end) for z in Z ] )
    else:
        y = _calc_y_of_kind(Z, ele, kind, t_end=t_end)

    return y


def _calc_y_of_kind(Z, ele, kind, t_end=10):
    yields = copy_current_yields(ele)
    if kind != "all":
        if -1 == kind.find("cc"):
            vice.yields.ccsne.settings[ele] = 0
        if -1 == kind.find("ia"):
            vice.yields.sneia.settings[ele] = 0
        if -1 == kind.find("agb"):
            vice.yields.agb.settings[ele] = ZeroAGB()

    y = _calc_y(Z, ele, t_end=t_end)
    reset_yields(ele, yields)

    return y

def _calc_y(Z, ele="c", t_end=10):
    m_c, times = vice.single_stellar_population(ele, Z=Z, mstar=1, time=t_end)
    return m_c[-1]


""" Copies the current yields for an element. Used for resetting after calculations
Returns the values of the yields from vice as a tuple for CCSNe, AGB, and SNe Ia
"""
def copy_current_yields(ele):
    ycc = vice.yields.ccsne.settings[ele]
    yagb = vice.yields.agb.settings[ele]
    yia = vice.yields.sneia.settings[ele]
    return ycc, yagb, yia


""" Resets the yields to the original values"""
def reset_yields(ele, yields):
    ycc, yagb, yia = yields

    vice.yields.ccsne.settings[ele] = ycc
    vice.yields.agb.settings[ele] = yagb
    vice.yields.sneia.settings[ele] = yia



