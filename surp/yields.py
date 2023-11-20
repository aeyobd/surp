import textwrap
from typing import Optional
from copy import copy

import numpy as np
from scipy.integrate import quad
from scipy.interpolate import interp1d

import vice
from vice.yields.agb import interpolator
from vice.yields import ccsne, sneia, agb

from surp._globals import Z_SUN
from surp.analysis import MH_to_Z
from surp.analysis import gce_math as gcem

from .utils import isreal, validate, arg_isreal



# Constants

ELEMS = ["c", "n", "o", "mg", "fe"]


Y_C_0 = 2.85e-3
ZETA_C_0 = 0.029
Y_C_AGB = {
        "cristallo11": 4.2e-4,
        "karakas10": 6.4e-4,
        "ventura13": 2.2e-4,
        "karakas16": 5.1e-4,
        "pignatari16": 8.1e-4,
        "A": 5e-4,
}

ZETA_C_AGB = {
        "cristallo11": -0.0175,
        "karakas10": -0.059,
        "ventura13": -0.021,
        "karakas16": -0.029,
        "pignatari16": -0.005,
}



def set_magg22_scale():
    """Sets the solar_z values of c, o, mg, fe, and n to magg++2022"""
    vice.solar_z["c"] = 0.00339
    vice.solar_z["o"] = 0.00733
    vice.solar_z["mg"] = 0.000671
    vice.solar_z["fe"] = 0.00137
    vice.solar_z["n"] = 0.00104
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


def set_yields(fe_ia_factor=1, yield_scale=1, **kwargs) -> None:
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
    set_magg22_scale()
    set_defaults()

    set_c_yields(**kwargs)

    enhance_fe_ia(fe_ia_factor)
    scale_yields(yield_scale)

    print_yields()
    print_yc_tot()



def set_c_yields(
    agb_model="cristallo11", 
    f_agb=0.2,
    alpha_agb: Optional[float] = None, 
    zeta_cc: Optional[float] = None, 
    yl_cc: float = 8.67e-4, 
    zl_cc: float = 0.008,
    zeta_agb: float = -0.03,
    mass_factor: float = 1,
    no_negative: bool = False,
    **kwargs
    ):
    """
    Parameters
    ----------
    agb_model
        One of the implimented AGB settings in VICE. Sets all AGB elements to the given value
    eta_factor
        The factor by which to multiply yields and outflows by (uniformly)
    zeta_c_cc
        If set, determines the zeta_c_cc value. Otherwise zeta_c_cc is calculated from the zeta_c_agb value and 

    fe_ia_factor: float 
    
    """

    y_c_agb = Y_C_AGB[agb_model]

    if alpha_agb is None:
        alpha_agb = f_agb * Y_C_0 /y_c_agb

    if agb_model != "A":
        zeta_agb = ZETA_C_AGB[agb_model]
    elif zeta_agb is None:
        raise ValueError("for analytic AGB model, zeta_agb must be specified")
    y_cc = Y_C_0 - alpha_agb * y_c_agb 

    print('using alpha_c_agb=', alpha_agb)


    if zeta_cc is None:
        zeta_cc = ZETA_C_0 - alpha_agb * zeta_agb

    if agb_model == "A":
        y0 = alpha_agb * Y_C_AGB["A"]
        agb.settings["c"] = C_AGB_MODEL(y0=y0, **kwargs)
    else:
        agb.settings["c"] = interpolator("c", agb_model, prefactor=alpha_agb, mass_factor=mass_factor, no_negative=no_negative)

    ccsne.settings["c"] = C_CC_model(zeta=zeta_cc, y0=y_cc, yl=yl_cc, zl=zl_cc)


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




class ZeroAGB:
    """A convenience class which represents a value of zero AGB yield"""
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return 0

    def __str__(self):
        return "0"

    def __repr__(self):
        return "0"

    
    @arg_isreal(1)
    def __imul__(self, scale):
        pass
    def __mul__(self, scale):
        other = copy(self)
        other.__imul__(scale)
        return other 

    def __rmul__(self, scale):
        return self.__mul__(scale)



class LinAGB:
    """
    A linear AGB model, used e.g. for nitrogen
    y(m, z) = eta m z
    """
    def __init__(self, eta, y0):
        self.eta = eta
        self.y0 = y0

    def __call__(self, M, Z):
        return M*self.y0 + M*Z/Z_SUN * self.eta

    def __str__(self):
        return f"{self.y0:0.2e} M + {self.eta:0.2e} M Z/Z0"

    @arg_isreal(1)
    def __imul__(self, scale):
        self.y0 *= scale
        self.eta *= scale

    def __mul__(self, scale):
        other = copy(self)
        other.__imul__(scale)
        return other 

    def __rmul__(self, scale):
        return self.__mul__(scale)


class C_AGB_MODEL:
    """
    An analytic version of AGB yields.

    Parameters
    ----------
    y_0: the yield at solar metallicity
    zeta: the metallicity dependence
    tau_agb: the agb dtd
    t_d: the minimum delay time
    """

    def __init__(self, y0 = 0.0004, zeta_agb=-0.02, 
            tau_agb=0.3, t_D = 0.15):

        self.tau_agb = tau_agb
        self.t_D = t_D
        self.y0 = y0
        self.zeta = zeta_agb

        self.mlr = vice.mlr.larson1974
        self.imf = vice.imf.kroupa
        m_low = 0.08
        m_high = 8
        A_imf = quad(lambda m: m*self.imf(m), m_low, 100)[0]

        self.A_agb = A_imf / quad(lambda m: m * self.imf(m) * self.y_unnorm(m), 
                m_low, m_high)[0]

    def R(self, t):
        """
        The delay time distribution of C enrichment
        """
        dt = t - self.t_D
        return np.where(dt < 0, 0,
                dt/self.tau_agb**2 * np.exp(-dt/self.tau_agb))


    def y_unnorm(self, m):
        return 1/m * m**-4.5 * 1/self.imf(m) * self.R(self.mlr(m))


    def __call__(self, m, Z):
        y = self.y0 + self.zeta*(Z-Z_SUN)
        return self.A_agb * y * self.y_unnorm(m) 


    @arg_isreal(1)
    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale

    def __mul__(self, scale):
        other = copy(self)
        other.__imul__(scale)
        return other 

    def __rmul__(self, scale):
        return self.__mul__(scale)

    def __str__(self):
        return f"({self.y0:0.2e} + {self.zeta:0.2e}(Z-Zo)), t_D={self.t_D:0.2f}, tau={self.tau_agb:0.2f}"


class C_CC_model:
    def __init__(self, zeta=0.1, y0=0.004, yl=8.67e-4, zl=0.008):
        self.y0 = y0
        self.zeta = zeta
        self.yl = yl
        self.zl = zl

        if zl > 0:
            y2 = zeta * (zl - Z_SUN) + y0
            self.zeta_l = (y2-yl)/(zl)
        else:
            self.zeta_l = 0
            self.zl = -1

    @arg_isreal(1)
    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        self.yl *= scale
        self.zeta_l *= scale

    def __mul__(self, scale):
        other = copy(self)
        other.__imul__(scale)
        return other

    def __rmul__(self, scale):
        return self.__mul__(scale)



    def __call__(self, Z):
        return np.where(Z >= self.zl, 
                self.y0 + self.zeta * (Z - Z_SUN), 
                self.yl + self.zeta_l * Z
                )

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} (Z-Z0), Z>={self.zl:0.2e}; {self.yl:0.2e} + {self.zeta_l:0.2e} Z, else"







def print_yields():
    """
    Debugging function to print the current yield settings
    """
    print("Yield settings")
    print_row("X", "Z_solar", "CC", "agb", "SN Ia")

    # print values
    for elem in ["c", "n", "o", "mg", "fe"]:
        print_row(elem, 
                vice.solar_z(elem),
                ccsne.settings[elem],
                agb.settings[elem],
                sneia.settings[elem])

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
    elif isinstance(yagb, C_AGB_MODEL):
        model = "A"
        y0_agb = yagb.y0
        zeta_agb = yagb.zeta

    print("agb_model: ", model)

    z_tot = zeta_cc + zeta_agb
    y_tot =  y0_agb + y0_cc
    f = y0_agb/y_tot

    print(f"{y_tot:0.6f} + {z_tot:0.6f} (Z-Zo)")
    print(f"f_agb = {f:0.4f}")
    print()
    print()


def print_row(*args, width=30, first_width=8, float_fmt="%0.2e"):
    """
    given a list of arguments, prints them in a table format
    """
    strings = []

    for i in range(len(args)):
        arg = args[i]
        if isinstance(arg, float):
            s = float_fmt % arg
        else:
            s = str(arg)
        strings.append(s)

    N = len(args)
    widths = np.full(N, width)
    widths[0] = first_width

    wrapped = [textwrap.wrap(s, width=w) for s, w in zip(strings, widths)]

    N_rows = np.max([len(wd) for wd in wrapped])
    padded = [wd + [''] * (N_rows - len(wd)) for wd in wrapped]

    fmt = "".join("{{:<{}}} ".format(w) for w in widths)

    for i in range(N_rows):
        print(fmt.format(*(col[i] for col in padded)))
    print()



# TODO find where this function actually belongs (probably analysis)
def agb_z_interp(N_points=500):
    """
    a convennience function which interpolates yields
    """
    ycc = vice.yields.ccsne.settings["c"]
    vice.yields.ccsne.settings["c"] = 0

    y_agb = []
    Zs = MH_to_Z(np.linspace(-6, 1, N_points))
    for Z in Zs:
        mc, times = vice.single_stellar_population("c", Z=Z)
        y_agb.append(mc[-1]/1e6)

    vice.yields.ccsne.settings["c"] = ycc
    return interp1d(Zs, y_agb, fill_value="extrapolate")


def y_c_total(Z):
    """Returns our adopted total C yield given Z"""
    return Y_C_0 + ZETA_C_0*(Z-Z_SUN)
