from typing import Optional
from copy import copy
from dataclasses import dataclass

import numpy as np
from scipy.integrate import quad
from scipy.interpolate import interp1d

import vice
from .agb_interpolator import interpolator
from vice.yields import ccsne, sneia, agb

from surp._globals import Z_SUN
from surp.yield_models import ZeroAGB, C_AGB_Model, C_CC_Model, LinAGB

from .utils import print_row


ELEMS = ["c", "n", "o", "mg", "fe"]

def y_c_total(Z):
    """Returns our adopted total C yield given Z"""
    return Y_C_0 + ZETA_C_0*(Z-Z_SUN)


Y_C_0 = 2.85e-3
ZETA_C_0 = 0.029

# comments from linear regression of sampled points
# regression ran on points with M_H > -1 except -1.5 for P16 and -2 for C11
Y_C_AGB = {
        "cristallo11": 3.8e-4, # 2.8 pm 0.5
        "ventura13": 2.1e-4, # 3.0 pm 1.3
        "karakas16": 3.6e-4, # 4.3 pm 0.6
        "pignatari16": 6.9e-4, # 7.5 pm 1.5
        "A": 5e-4,
}

ZETA_C_AGB = {
        "cristallo11": -0.01, # -0.032 pm 0.004
        "ventura13": -0.04, #  -0.04 pm 0.01
        "karakas16": -0.04, # -0.04 pm 0.006
        "pignatari16": -0.01, # -0.010 pm 0.16
}



def set_magg22_scale(verbose=True):
    """Sets the solar_z values of c, o, mg, fe, and n to magg++2022"""
    vice.solar_z["c"] = 0.00339
    vice.solar_z["o"] = 0.00733
    vice.solar_z["mg"] = 0.000671
    vice.solar_z["fe"] = 0.00137
    vice.solar_z["n"] = 0.00104
    if verbose:
        print("yields set to Magg et al. 2022 abundances")



def set_defaults() -> None:
    """Sets the constant default yield settings used in the carbon paper"""
    sneia.settings["c"] = 0

    ccsne.settings["o"] = 7.13e-3
    sneia.settings["o"] = 0
    agb.settings["o"] = ZeroAGB()

    ccsne.settings["fe"] = 4.73e-4
    sneia.settings["fe"] = 7.7e-4 
    agb.settings["fe"] = ZeroAGB()

    ccsne.settings["mg"] = 6.52e-4
    sneia.settings["mg"] = 0
    agb.settings["mg"] = ZeroAGB()

    agb.settings["n"] = LinAGB(eta=5.02e-4, y0=0)
    ccsne.settings["n"] = 5e-4
    sneia.settings["n"] = 0



@dataclass
class YieldParams:
    agb_model:float
    alpha_agb:float
    f_agb:float
    zeta_cc:float
    fe_ia_factor:float
    mass_factor:float
    no_negative:float
    yl:float
    zl:float
    agb_n_model:float

    t_D:float
    tau_agb:float
    zeta_agb:float


def set_yields(fe_ia_factor=1, yield_scale=1,verbose=True, agb_n_model=None, **kwargs) -> None:
    """
    Ses the yields and abundace scale for the C project. 

    Params
    ------
    fe_ia_factor
        The factor to enhance SNeIa Fe by.
    yield_scale
        if set, scales all yields by the given factor

    **kwargs
        passed to set_c_yields
    
    """
    set_magg22_scale(verbose=verbose)
    set_defaults()

    set_c_yields(**kwargs)
    set_n_yields(agb_n_model)

    enhance_fe_ia(fe_ia_factor)
    scale_yields(yield_scale)

    if verbose:
        print_yields()
        print_yc_tot()


def set_n_yields(agb_model=None):
    if agb_model is not None:
        agb.settings["n"] = interpolator("n", study=agb_model)


def set_c_yields(
    agb_model="cristallo11", 
    f_agb=0.2,
    zeta_cc: Optional[float] = None, 
    alpha_agb: Optional[float] = None, 
    mass_factor: float = 1,
    no_negative: bool = False,
    a_agb_kwargs: dict = {},
    interp_kind: str = "linear",
    **kwargs
    ):
    """
    Interdependent Parameters
    ------------------------
    agb_model
        One of the implimented AGB settings in VICE. Sets all AGB elements to the given value
    f_agb
        the AGB fraction of C production at solar metallicity
    zeta_cc
        If set, determines the zeta_cc value. Otherwise zeta_cc is calculated from the zeta_c_agb value and the
        total ZETA_C_0 value

    CCSNe Parameters
    -----------------
    **kwargs are passed to yield_models.C_CC_Model

    yl_cc
        Determines the CC yield at zero metallicity (if zl_cc > 0)
    zl_cc
        Below this metallicity, the CC yield linearly decreases to yl_cc

    AGB Parameters
    --------------
    mass_factor

    """

    y_c_agb = Y_C_AGB[agb_model]

    if alpha_agb is None:
        alpha_agb = f_agb * Y_C_0 /y_c_agb


    if agb_model == "A":
        if "zeta_agb" not in a_agb_kwargs.keys():
            raise ValueError("for analytic AGB model, zeta_agb must be specified")

        y0 = alpha_agb * y_c_agb
        zeta_agb = a_agb_kwargs["zeta_agb"]
        a_agb_kwargs["zeta_agb"] *= alpha_agb
        agb.settings["c"] = C_AGB_Model(y0=y0, **a_agb_kwargs)
    else:
        agb.settings["c"] = interpolator("c", agb_model, prefactor=alpha_agb,
            mass_factor=mass_factor, no_negative=no_negative, interp_kind=interp_kind)
        zeta_agb = ZETA_C_AGB[agb_model]


    y_cc = Y_C_0 - alpha_agb * y_c_agb 
    if zeta_cc is None:
        zeta_cc = ZETA_C_0 - alpha_agb * zeta_agb

    ccsne.settings["c"] = C_CC_Model(zeta=zeta_cc, y0=y_cc, **kwargs)


def enhance_fe_ia(fe_ia_factor=1):
    """Sets the Fe settings, possibly with an Ia enhancement factor"""
    if fe_ia_factor == 1:
        return
    fe_total = sneia.settings["fe"] + ccsne.settings["fe"]
    fe_ia = sneia.settings["fe"] * fe_ia_factor
    fe_cc = fe_total - fe_ia
    ccsne.settings["fe"] = fe_cc
    sneia.settings["fe"] = fe_ia



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


def print_yc_tot():
    """prints out the current total c yield"""

    print('total c yield')

    ycc = ccsne.settings["c"]
    yagb = agb.settings["c"]

    y0_cc = ycc.y0
    zeta_cc = ycc.zeta

    if isinstance(yagb, agb.interpolator):
        model = yagb.study
        alpha = yagb.prefactor
        y0_agb = alpha * Y_C_AGB[model]
        zeta_agb = alpha * ZETA_C_AGB[model]
        print("y0_agb ", Y_C_AGB[model])
        print("z0_agb ", ZETA_C_AGB[model])
    elif isinstance(yagb, C_AGB_Model):
        model = "A"
        y0_agb = yagb.y0
        zeta_agb = yagb.zeta
        print("Y agb", y0_agb)
        print("zeta agb", zeta_agb)

    print("agb_model: ", model)

    z_tot = zeta_cc + zeta_agb
    y_tot =  y0_agb + y0_cc
    f = y0_agb/y_tot

    print(f"{y_tot:0.6f} + {z_tot:0.6f} (Z-Zo)")
    print(f"f_agb = {f:0.4f}")
    print()
    print()




