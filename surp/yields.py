import vice
import numpy as np
from vice.yields.agb import interpolator
from scipy.integrate import quad
from vice.yields import ccsne, sneia, agb



# Constants
Z_Sun = 0.014

Y_C_0 = 0.005
ZETA_0 = 0.06

y_n_flat = 7.2e-4


Y_AGB = {
        "cristallo11": 4.2e-4,
        "karakas10": 6.4e-4,
        "ventura13": 2.2e-4,
        "karakas16": 5.1e-4,
        "A": 5e-4,
}

ZETA_AGB = {
        "cristallo11": -0.0175,
        "karakas10": -0.059,
        "ventura13": -0.021,
        "karakas16": -0.029,
}

# default settings


def set_yields(eta=1, zeta=None, fe_ia_factor=None,
               agb_model="cristallo11", oob=False, f_agb=0.2,
               alpha_n=0, 
               mass_factor=1,
               zeta_agb=-0.03,
               **kwargs
              ):
    """
    Parameters
    ----------

    eta
    
    """

    set_fe(fe_ia_factor)

    alpha_agb = calc_alpha(agb_model, oob, f_agb)
    y_cc = calc_ycc(agb_model, alpha_agb)
    if zeta is None:
        zeta = calc_zeta(agb_model, alpha_agb, zeta_agb)

    # correct ...
    alpha_agb *= eta
    y_cc *= eta
    zeta *= eta

    set_agb(agb_model, alpha_agb, mass_factor, zeta_agb=zeta_agb, **kwargs)

    set_n(eta, alpha_n)
    
    vice.yields.ccsne.settings["c"] = C_CC_model(zeta=zeta, y0=y_cc)

    set_eta(eta)

    set_isotopic()

    print_yields()




def set_isotopic():
    vice.yields.sneia.settings["au"] = 0
    vice.yields.ccsne.settings["au"] = 0
    vice.yields.agb.settings["au"] = lambda m, z: 0
    vice.yields.sneia.settings["ag"] = 0
    vice.yields.ccsne.settings["ag"] = 0
    vice.yields.agb.settings["ag"] = lambda m, z: 0

class LinAGB:
    def __init__(self, zeta, y0):
        self.zeta = zeta
        self.y0 = y0

    def __call__(self, M, Z):
        return M*self.y0 + M*Z/Z_Sun * self.zeta

    def __str__(self):
        return f"{self.y0:0.2e} M + {self.zeta:0.2e} M Z/Z0"




class C_CC_model:
    def __init__(self, zeta=0.1, y0=0.004, pop_iii=0.2, Z_iii=10**(-5.5)):
        # defaults
        # zeta = 0.70
        # y0 = 0.004
        # Z_iii = 10**-5.5
        # pop_iii = 0.005
        self.y0 = y0
        self.zeta = zeta
        self.pop_iii = pop_iii
        self.Z_iii = Z_iii

    def __call__(self, Z):
        return (self.y0 
            + self.zeta * (Z - Z_Sun)
            + self.y0 * self.pop_iii*2/(1 + Z/self.Z_iii))

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} (Z - Z0)"



def set_defaults():
    ccsne.settings["o"] = 0.015
    sneia.settings["o"] = 0

    ccsne.settings["fe"] = 0.0012
    sneia.settings["fe"] = 0.0017
    # sneia.settings["fe"] *= 10**0.1 # correction for mdf, used in

    ccsne.settings["sr"] = 3.5e-8
    sneia.settings["sr"] = 0

    ccsne.settings["n"] = 3.6e-4

    sneia.settings["c"] = 0
    sneia.settings["n"] = 0

    ccsne.settings["mg"] = 0.00185
    sneia.settings["mg"] = 0

set_defaults()




def set_agb_elem(elem, study, factor, **kwargs):
    if study == "A":
        study = "cristallo11"

    if elem == "fe" and agb_model == "ventura13":
        study = "cristallo11"

    agb.settings[elem] = interpolator(elem, study, prefactor=factor, **kwargs)



def set_agb(study="cristallo11", factor=1, mass_factor=1, **kwargs):
    for elem in ["c", "o", "mg"]:
        set_agb_elem(elem, study, factor, mass_factor=mass_factor)

    if study == "A":
        agb.settings["c"] = a_agb(ym_agb=factor * Y_AGB["A"], **kwargs)


def set_fe(fe_ia_factor):
    if fe_ia_factor:
        fe_total = vice.yields.sneia.settings["fe"] + vice.yields.ccsne.settings["fe"]
        fe_ia = vice.yields.sneia.settings["fe"] * fe_ia_factor
        fe_cc = fe_total - fe_ia
        vice.yields.ccsne.settings["fe"] = fe_cc
        vice.yields.sneia.settings["fe"] = fe_ia



def set_eta(eta=1):
    if eta==1:
        return

    for elem in ["o", "fe", "mg", "sr", "n"]:
        y = ccsne.settings[elem] 
        if isinstance(y, float):
            ccsne.settings[elem] *= eta

        y = sneia.settings[elem] 
        if isinstance(y, float):
            sneia.settings[elem] *= eta


def set_n(eta, alpha_n):
    y_cc_n = eta*y_n_flat * (1-alpha_n)
    y_n_0 = eta*y_n_flat * alpha_n
    vice.yields.agb.settings["n"] = LinAGB(zeta=9e-4, y0=y_n_0)
    vice.yields.ccsne.settings["n"] = y_cc_n





def calc_alpha(agb_model="cristallo11" , oob=False, f_agb=0.2):
    y_agb = Y_AGB[agb_model]
    if oob:
        alpha = 1
    else:
        alpha = f_agb * Y_C_0 /y_agb
    return alpha


def calc_ycc(agb_model, alpha_agb):
    y_agb = Y_AGB[agb_model]

    y_cc = Y_C_0 - alpha_agb * y_agb 
    return y_cc


def calc_zeta(agb_model, alpha_agb, zeta_agb):
    if agb_model != "A":
        zeta_agb = alpha_agb * ZETA_AGB[agb_model]

    return ZETA_0 - zeta_agb


def a_agb(m_low=1.3, m_mid=None, m_high=4, yl_agb=0, ym_agb=5e-4, yh_agb=0,
        zeta_agb=-0.03):
    """
    An analytic version of AGB yields.

    Parameters
    ----------
    m_low: the beginning of the cubic spline.
    m_mid: the peak mass. If None, defaults to the average of m_low and m_high
    m_high: the end of the cubic spline. 
    yl_agb: the yield at m_low
    ym_agb: the total yield
    yh_agb: the yield at m_high 
    zeta_agb: the metallicity dependent part of the yield at ym_agb
    """
    if m_mid is None:
        m_mid = (m_low + m_high)/2

    def y_spline(m):
        return spline(m, [m_low, m_mid, m_high], [yl_agb, ym_agb, yh_agb])


    imf_norm = quad(lambda m: m*vice.imf.kroupa(m), 0.08, 100)[0]

    def f(m):
        return m * vice.imf.kroupa(m)/imf_norm * y_spline(m)

    A_agb = 1 / quad(f, m_low, m_high)[0]

    def inner(m, z):
        if z > 0:
            m_h = np.log10(z/Z_Sun)
        elif z == 0:
            m_h = -8
        else:
            print("warning, negative z, z=", z)
        return A_agb * y_spline(m) * (ym_agb + zeta_agb * (z - Z_Sun) )
    return inner



def sspline(x):
    if x < 0 or 1 < x:
        return 0
    return 3*x**2 - 2*x**3

def pspline(x, x0, y0):
    m = y0[1] - y0[0]
    if x0[0] <= x <= x0[1]:
        return y0[0] + m*sspline( (x-x0[0])/(x0[1] - x0[0]) )
    else:
        return 0


def spline(x, xs, ys):
    s = 0

    if x < xs[0]:
        return ys[0]
    if x > xs[-1]:
        return ys[-1]

    for i in range(len(xs) - 1):
        x0 = (xs[i], xs[i+1])
        y0 = (ys[i], ys[i+1])
        s += pspline(x, x0, y0)
        
    return s


def print_yields():
    # print header
    print("Yield settings")
    print_row("X", "CC", "agb", "SN Ia")

    # print values
    for elem in ["c", "n", "o", "mg", "fe"]:
        print_row(elem, 
                ccsne.settings[elem],
                agb.settings[elem],
                sneia.settings[elem])

    print()
    print()



def print_row(*args):
    for i in range(len(args)):
        arg = args[i]
        if isinstance(arg, float):
            s = "%0.2e" % arg
        else:
            s = str(arg)

        if i==0:
            print(f"{s:8}", end="")
        elif i==(len(args)-1):
            print(f"{s}", end="")
        else:
            print(f"{s:30}", end="")
    print()

