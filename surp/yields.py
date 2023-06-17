import vice
import numpy as np
from vice.yields.agb import interpolator
from scipy.integrate import quad
from vice.yields import ccsne, sneia, agb


Z_Sun = 0.014
y_c_0 = 0.005
y_c_cc_0=0.0028
y_n_flat = 7.2e-4



YC_AGB0 = {
        "cristallo11": 3.47e-4,
        "karakas10": 5.85e-4,
        "ventura13": 6.0e-5,
        "karakas16": 4.21e-4,
        "A": 5e-4,
}

# default settings


def set_yields(eta=1, beta=0.001, fe_ia_factor=None,
               agb_model="cristallo11", oob=False, f_agb=0.2,
               alpha_n=0, 
               **kwargs
              ):

    set_fe(fe_ia_factor)

    alpha_agb, alpha_cc = calc_alpha(agb_model, eta, oob, f_agb)
    set_agb(agb_model, alpha_agb, **kwargs)

    set_n(eta, alpha_n)
    
    prefactor = y_c_0 * alpha_cc / (y_c_cc_0 + beta)
    vice.yields.ccsne.settings["c"] = LinCC(zeta=beta*prefactor, y0=prefactor*y_c_cc_0)

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




class LinCC:
    def __init__(self, zeta, y0):
        self.zeta = zeta
        self.y0 = y0

    def __call__(self, Z):
        return self.y0 + self.zeta*(Z/Z_Sun) 

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} Z/Z0"


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




def set_agb_elem(elem, study, factor, mass_factor=1, **kwargs):
    if study == "A":
        study = "cristallo11"

    if elem == "fe" and agb_model == "ventura13":
        study = "cristallo11"

    if mass_factor != 1:
        agb.settings[elem] = (lambda m, z: 
                interpolator(elem, study, prefactor=factor)(
                    m*mass_factor, z)
                )
    else:
        agb.settings[elem] = interpolator(elem, study, prefactor=factor)



def set_agb(study="cristallo11", factor=1, **kwargs):
    for elem in ["c", "o", "mg"]:
        set_agb_elem(elem, study, factor, **kwargs)

    if study == "A":
        agb.settings["c"] = lambda m, z: factor * a_agb(**kwargs)(m, z)


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

    for elem in ["o", "fe", "mg", "sr", "n", "c"]:
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





def calc_alpha(agb_model="cristallo11" , eta=1, oob=False, f_agb=0.2):
    y_agb = YC_AGB0[agb_model]
    y_c = y_c_0 * eta

    if oob:
        alpha_agb = 1
        f_agb = YC_AGB0[agb_model]/y_c_0
    else:
        alpha_agb = f_agb*y_c/y_agb

    alpha_cc = eta * (1 - f_agb)

    return alpha_agb, alpha_cc


def a_agb(m_low=1.3, m_mid=None, m_high=4, yl_agb=0, ym_agb=5e-4, yh_agb=0,
        mz_agb=-4e-4):
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
    mz_agb: the metallicity dependent part of the yield at ym_agb
    """
    if m_mid is None:
        m_mid = (m_low + m_high)/2

    def y_spline(m, z=0.014):
        if z > 0:
            m_h = np.log10(z/Z_Sun)
        elif z == 0:
            m_h = -8
        else:
            print("warning, negative z, z=", z)

        return spline(m, [m_low, m_mid, m_high], [yl_agb, ym_agb + mz_agb*m_h, yh_agb])

    imf_norm = quad(lambda m: m*vice.imf.kroupa(m), 0.08, 100)[0]

    def f(m):
        return m * vice.imf.kroupa(m)/imf_norm * y_spline(m)

    A_agb = ym_agb / quad(f, m_low, m_high)[0]

    def inner(m, z):
        return A_agb * y_spline(m, z)
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

