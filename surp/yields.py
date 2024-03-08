from dataclasses import dataclass, field, asdict
import json

import vice
from vice.yields import ccsne, sneia, agb

from surp._globals import Z_SUN
from surp.yield_models import ZeroAGB, C_AGB_Model, C_CC_Model, LinAGB

from .utils import print_row
from .agb_interpolator import interpolator


ELEMS = ["c", "n", "o", "mg", "fe"]


@dataclass
class YieldParams:
    c_cc_y0:float = None # these need specified, but initialize anyways
    c_cc_zeta:float = None
    c_cc_model:str = "A"
    c_cc_y1:float = 0
    c_cc_z1:float = 0

    c_agb_model:str = "cristallo11"
    c_agb_alpha:float = 1
    c_agb_kwargs:dict = field(default_factory=dict)

    n_agb_model:str = "A"
    n_agb_eta:float = 5.02e-4
    n_agb_y0:float = 0
    n_cc_y0: float = 5e-4
    n_cc_zeta: float = 0

    fe_ia: float = 7.7e-4
    fe_cc: float = 4.73e-4

    def to_dict(self):
        return asdict(self)

    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)


    @classmethod
    def from_file(cls, filename):
        with open(filename, "r") as f:
            params = json.load(f)
        return cls(**params)



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
    # ccsne.settings["c"]
    # agb.settings["c"]

    ccsne.settings["o"] = 7.13e-3
    sneia.settings["o"] = 0
    agb.settings["o"] = ZeroAGB()

    # ccsne.settings["fe"] = 
    # sneia.settings["fe"] = 7.7e-4 
    agb.settings["fe"] = ZeroAGB()

    ccsne.settings["mg"] = 6.52e-4
    sneia.settings["mg"] = 0
    agb.settings["mg"] = ZeroAGB()

    #agb.settings["n"] = LinAGB(eta=5.02e-4, y0=0)
    #ccsne.settings["n"] = 5e-4
    sneia.settings["n"] = 0



def set_yields(params:YieldParams, verbose=False):
    """ Ses the yields and abundace scale for the C project. """
    set_magg22_scale(verbose=verbose)
    set_defaults()

    agb.settings["c"] = get_c_agb_model(params)
    ccsne.settings["c"] = get_c_cc_model(params)

    agb.settings["n"] = get_n_agb_model(params)
    ccsne.settings["n"] = params.n_cc_y0

    sneia.settings["fe"] = params.fe_ia
    ccsne.settings["fe"] = params.fe_cc

    if verbose:
        print_yields()


def get_c_agb_model(params):
    if params.c_agb_model == "A":
        model = C_AGB_Model(**params.c_agb_kwargs)
    else:
        model = interpolator("c", study=params.c_agb_model, **params.c_agb_kwargs)

    model *= params.c_agb_alpha
    return model


def get_c_cc_model(params):
    if params.c_cc_model == "A":
        model = C_CC_Model(y0=params.c_cc_y0, zeta=params.c_cc_zeta, 
            zl=params.c_cc_z1, yl=params.c_cc_y1)
    else:
        model = params.c_cc_model

    return model


def get_n_agb_model(params):
    if params.n_agb_model == "A":
        model = LinAGB(eta=params.n_agb_eta, y0=params.n_agb_y0)
    else:
        model = params.n_agb_model

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



def calc_y(Z=Z_SUN, ele="c"):
    m_c, times = vice.single_stellar_population(ele, Z=Z, mstar=1)
    return m_c[-1]
