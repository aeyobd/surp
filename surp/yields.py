import vice
from vice.yields import ccsne, sneia, agb

from surp._globals import Z_SUN
from surp import yield_models

from .utils import print_row
from .agb_interpolator import interpolator
from .yield_params import YieldParams


ELEMS = ["c", "n", "o", "mg", "fe"]



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



def set_yields(params=YieldParams(), verbose=False, **kwargs):
    """ 
    set_yields(params, verbose=False, **kwargs)
    Ses the yields and abundace scale for the C project. """

    params = params.to_dict()
    for key, val in kwargs.items():
        params[key] = val
    params = YieldParams(**params)

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
    """Returns an AGB model for C with properties specified in params"""
    if params.c_agb_model == "A":
        model = yield_models.C_AGB_Model(**params.c_agb_kwargs)
    else:
        model = interpolator("c", study=params.c_agb_model, **params.c_agb_kwargs)

    model *= params.c_agb_alpha
    return model


def get_c_cc_model(params):
    """Returns a CC model for C with properties specified in params"""
    if params.c_cc_model == "BiLin":
        model = yield_models.BiLin_CC(y0=params.c_cc_y0, zeta=params.c_cc_zeta, **params.c_cc_kwargs)
    elif params.c_cc_model == "Lin":
        model = yield_models.Lin_CC(y0=params.c_cc_y0, zeta=params.c_cc_zeta)
    elif params.c_cc_model == "LogLin":
        model = yield_models.LogLin_CC(y0=params.c_cc_y0, B=params.c_cc_zeta, **params.c_cc_kwargs)
    elif params.c_cc_model == "BiLogLin":
        model = yield_models.BiLogLin_CC(y0=params.c_cc_y0, B=params.c_cc_zeta, **params.c_cc_kwargs)
    elif params.c_cc_model == "Quadratic":
        model = yield_models.Quadratic_CC(y0=params.c_cc_y0, B=params.c_cc_zeta, **params.c_cc_kwargs)
    else:
        model = params.c_cc_model

    return model


def get_n_agb_model(params):
    if params.n_agb_model == "A":
        model = yield_models.LinAGB(eta=params.n_agb_eta, y0=params.n_agb_y0)
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



