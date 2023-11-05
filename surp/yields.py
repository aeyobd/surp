import vice
import numpy as np
from vice.yields.agb import interpolator
from scipy.integrate import quad
from scipy.interpolate import interp1d
from vice.yields import ccsne, sneia, agb

from surp._globals import Z_SUN
from surp.analysis import MH_to_Z
from surp.analysis import gce_math as gcem



# Constants
Y_C_0 = 2.85e-3 # 5e-3
Y_C_MIN = 14.15e-4

ZETA_0 = 0.029 # 0.06
ZETA_X = -0.023
y_n_flat = 5e-4
ZETA_N = 5.02e-4
Z_III = Z_SUN * 10**-4


XI_0 = 6.52e-4
DZETA_DXI = -0.008


def y_c_total(Z):
    return Y_C_0 + ZETA_0*(Z-Z_SUN) + XI_0 * (Z-Z_SUN)**2

Y_AGB = {
        "cristallo11": 4.2e-4,
        "karakas10": 6.4e-4,
        "ventura13": 2.2e-4,
        "karakas16": 5.1e-4,
        "pignatari16": 8.1e-4,
        "A": 5e-4,
}
ZETA_AGB = {
        "cristallo11": -0.0175,
        "karakas10": -0.059,
        "ventura13": -0.021,
        "karakas16": -0.029,
        "pignatari16": -0.005,
}

Y_AGB_X = {
        "cristallo11": 3.6e-4,
        "ventura13": 1.8e-4,
        "karakas16": 3.7e-4,
        "pignatari16": 7.6e-4,
}

ZETA_AGB_X = {
        "cristallo11": -0.0128,
        "ventura13": -0.041,
        "karakas16": -0.036,
        "pignatari16": -0.0057,
}


# default settings

def magg_22():
    vice.solar_z["c"] = 0.00339
    vice.solar_z["o"] = 0.00733
    vice.solar_z["mg"] = 0.000671
    vice.solar_z["fe"] = 0.00137
    vice.solar_z["n"] = 0.00104
    print("modified solar abundances via mag++22")

magg_22()

def set_yields(eta=1, zeta=None, fe_ia_factor=None,
               agb_model="cristallo11", oob=False, f_agb=0.2,
               alpha_n=0, 
               gamma=1,
               mass_factor=1,
               zeta_agb=-0.03,
               xi=None,
               y1_cc=8.67e-4, 
               y2_cc=-0e-3,
               z1_cc=0.008,
               z2_cc=3e-3,
               fix_total=False,
               log_cc=False,
               **kwargs
              ):
    """
    Parameters
    ----------

    eta
    
    """
    set_defaults()

    set_fe(fe_ia_factor)


    if xi is None:
        xi = 0

    alpha_agb = calc_alpha(agb_model, oob, f_agb, xi)
    if not fix_total:
        y_cc = calc_ycc(agb_model, alpha_agb)
        if zeta is None:
            zeta = calc_zeta(agb_model, alpha_agb, zeta_agb, xi)
        y_cc *= eta
        zeta *= eta

    if log_cc:
        xi = XI_0
        zeta += ZETA_X - ZETA_0
        y_cc += Y_C_MIN - Y_C_0
    alpha_agb *= eta

    set_agb(agb_model, alpha_agb, mass_factor, zeta_agb=zeta_agb, **kwargs)

    set_n(eta, alpha_n)
    

    # if fix_total:
    #     y_agb = agb_z_interp()
    #     def y_c_cc(Z):
    #         return eta * (y_c_total(Z) - y_agb(Z))
    #     vice.yields.ccsne.settings["c"] = y_c_cc
    # else:
    vice.yields.ccsne.settings["c"] = C_CC_model(zeta=zeta, y0=y_cc,
            y1=y1_cc,  z1=z1_cc)


    set_eta(eta)
    print_yields()


def agb_z_interp(N_points=500):
    ycc = vice.yields.ccsne.settings["c"]
    vice.yields.ccsne.settings["c"] = 0

    y_agb = []
    Zs = MH_to_Z(np.linspace(-6, 1, N_points))
    for Z in Zs:
        mc, times = vice.single_stellar_population("c", Z=Z)
        y_agb.append(mc[-1]/1e6)

    vice.yields.ccsne.settings["c"] = ycc
    return interp1d(Zs, y_agb, fill_value="extrapolate")




class LinAGB:
    def __init__(self, zeta, y0):
        self.zeta = zeta
        self.y0 = y0

    def __call__(self, M, Z):
        return M*self.y0 + M*Z/Z_SUN * self.zeta

    def __str__(self):
        return f"{self.y0:0.2e} M + {self.zeta:0.2e} M Z/Z0"




class C_CC_model:
    def __init__(self, zeta=0.1, y0=0.004, y1=8.67e-4, z1=0.008):
        self.y0 = y0
        self.zeta = zeta
        self.y1 = y1
        self.z1 = z1
        y2 = zeta * (z1 - Z_SUN) + y0
        self.zeta2 = (y2-y1)/(z1-0)



    def __call__(self, Z):
        mh = gcem.Z_to_MH(np.maximum(Z, self.z1))
        return np.where(Z > self.z1, 
                self.y0 + self.zeta * (Z - Z_SUN), 
                self.y1 + self.zeta2 * Z
                )

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} (Z - Z0), Z<{self.z1:0.2e}\r {self.y1:0.2e} + {self.zeta2:0.2e} Z, else"



class ZeroAGB:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return 0

    def __str__(self):
        return "0"

    def __repr__(self):
        return "0"

def set_defaults():
    sneia.settings["c"] = 0

    ccsne.settings["o"] = 7.13e-3 # 0.015
    sneia.settings["o"] = 0
    agb.settings["o"] = ZeroAGB()

    ccsne.settings["fe"] = 4.73e-4 # 12e-4
    sneia.settings["fe"] = 7.7e-4 # 17e-4
    agb.settings["fe"] = ZeroAGB()

    ccsne.settings["sr"] = 3.5e-8
    sneia.settings["sr"] = 0

    ccsne.settings["mg"] = 6.52e-4 # 0.00185
    sneia.settings["mg"] = 0
    agb.settings["mg"] = ZeroAGB()





def set_agb_elem(elem, study, factor, **kwargs):
    if study == "A":
        study = "cristallo11"

    if elem == "fe" and agb_model == "ventura13":
        study = "cristallo11"

    agb.settings[elem] = interpolator(elem, study, prefactor=factor, **kwargs)



def set_agb(study="cristallo11", factor=1, mass_factor=1, no_negative=False, **kwargs):
    for elem in ["c"]:
        set_agb_elem(elem, study, factor, mass_factor=mass_factor, no_negative=no_negative)

    if study == "A":
        agb.settings["c"] = a_agb(y_agb_0=factor * Y_AGB["A"], **kwargs)


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
    vice.yields.agb.settings["n"] = LinAGB(zeta=ZETA_N, y0=y_n_0)
    vice.yields.ccsne.settings["n"] = y_cc_n





def calc_alpha(agb_model="cristallo11" , oob=False, f_agb=0.2, xi=0):
    y_agb = Y_AGB[agb_model]
    # if xi != 0:
    #     y_agb += (Y_AGB_X[agb_model] - Y_AGB[agb_model]) * xi
    if oob:
        alpha = 1
    else:
        alpha = f_agb * Y_C_0 /y_agb
    return alpha


def calc_ycc(agb_model, alpha_agb):
    y_agb = Y_AGB[agb_model]

    y_cc = Y_C_0 - alpha_agb * y_agb 
    return y_cc


def calc_zeta(agb_model, alpha_agb, zeta_agb, xi):
    if agb_model != "A":
        zeta_agb = ZETA_AGB[agb_model]
    return ZETA_0 - alpha_agb * zeta_agb



def a_agb(y_agb_0 = 0.004, zeta_agb=0.1, tau_agb=0.3, t_D = 0.15):
    """
    An analytic version of AGB yields.

    Parameters
    ----------
    y_0: the yield at solar metallicity
    zeta: the metallicity dependence
    tau_agb: the agb dtd
    t_d: the minimum delay time
    """

    mlr = vice.mlr.larson1974
    imf = vice.imf.kroupa
    m_low = 0.08
    m_high = 8

    def R(t):
        dt = t - t_D
        return np.where(dt < 0, 0,
                dt/tau_agb**2 * np.exp(-dt/tau_agb))


    A_imf = quad(lambda m: m*imf(m), m_low, 100)[0]

    def y_unnorm(m):
        return 1/m * m**-4.5 * 1/imf(m) * R(mlr(m))

    A_agb = A_imf / quad(lambda m: imf(m) * m *y_unnorm(m), m_low, m_high)[0]

    def y(m, z):
        return A_agb * y_unnorm(m) * (y_agb_0 + zeta_agb*(z-Z_SUN))
    return y



def print_yields():
    """
    Debugging function to print the current yield settings
    """
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



def print_row(*args, width=30, first_width=8, float_fmt="%0.2e"):
    """
    given a list of arguments, prints them in a table format
    """
    for i in range(len(args)):
        arg = args[i]
        if isinstance(arg, float):
            s = float_fmt % arg
        else:
            s = str(arg)

        if i==0:
            w = first_width
        else:
            w = width

        fmt = f"{{s:{w}}}" 

        out_s = fmt.format(arg) 
        print(out_s, end=" ")
    print()



# def sspline(x):
#     if x < 0 or 1 < x:
#         return 0
#     return 3*x**2 - 2*x**3
# 
# def pspline(x, x0, y0):
#     m = y0[1] - y0[0]
#     if x0[0] <= x <= x0[1]:
#         return y0[0] + m*sspline( (x-x0[0])/(x0[1] - x0[0]) )
#     else:
#         return 0
# 
# 
# def spline(x, xs, ys):
#     s = 0
# 
#     if x < xs[0]:
#         return ys[0]
#     if x > xs[-1]:
#         return ys[-1]
# 
#     for i in range(len(xs) - 1):
#         x0 = (xs[i], xs[i+1])
#         y0 = (ys[i], ys[i+1])
#         s += pspline(x, x0, y0)
#         
#     return s
#  def set_isotopic():
#      vice.yields.sneia.settings["au"] = 0
#      vice.yields.ccsne.settings["au"] = 0
#      vice.yields.agb.settings["au"] = lambda m, z: 0
#      vice.yields.sneia.settings["ag"] = 0
#      vice.yields.ccsne.settings["ag"] = 0
#      vice.yields.agb.settings["ag"] = lambda m, z: 0
