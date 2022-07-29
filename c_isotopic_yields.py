import vice
import pandas as pd
import numpy as np
from scipy.integrate import quad

# we use ua as c12 and ag as c13

def set_agb_yields():
    agb = pd.read_csv("c_isotope_fruitty.txt", sep="\s+")
    agb["C12"] /= agb["Mass"]
    agb["C13"] /= agb["Mass"]

    df = agb
    df = df[df["Metallicity"] > 0.00005]

    def set_isotope(col, ele):
        c12 = df.pivot("Mass", "Metallicity", col)
        M = c12.index.to_list()
        Z = c12.columns.to_list()
        vice.yields.agb.settings[ele] = vice.toolkit.interpolation.interp_scheme_2d(M, Z, c12.to_numpy())

    set_isotope("C12", "au")
    set_isotope("C13", "ag")

    vice.yields.sneia.settings["au"] = 0
    vice.yields.sneia.settings["ag"] = 0
    
def set_cc_yields():
    imf = vice.imf.kroupa
    imf_norm = quad(lambda m: imf(m)*m, 0.008, 100)[0]
    m_min = 8
    m_max = 100

    vrot = 0
    yields_c12 = []
    yields_c13 = []
    MoverH = [-3, -2, -1, 0]

    for M_H in MoverH:
        t = vice.yields.ccsne.table("c", study="LC18", isotopic=True, MoverH=M_H)
        
        f = vice.toolkit.interpolation.interp_scheme_1d(t.masses, [t[m]["c13"] for m in t.masses])
        y_c13_cc = quad(lambda m: imf(m) * f(m), m_min, m_max)[0] / imf_norm
        yields_c13.append(y_c13_cc)
        
        f = vice.toolkit.interpolation.interp_scheme_1d(t.masses, [t[m]["c12"] for m in t.masses])
        y_c12_cc = quad(lambda m: imf(m) * f(m), m_min, m_max)[0] / imf_norm
        yields_c12.append(y_c12_cc)

    Z = [0.014 * 10**M_H for M_H in MoverH]
    y_c = [vice.yields.ccsne.fractional("c", MoverH=M_H, rotation=0, study="LC18")[0] for M_H in MoverH]
    
    vice.yields.ccsne.settings["C"] = vice.toolkit.interpolation.interp_scheme_1d(Z, y_c)
    
    vice.yields.ccsne.settings["au"] = vice.toolkit.interpolation.interp_scheme_1d(Z, yields_c12)
    vice.yields.ccsne.settings["ag"] = vice.toolkit.interpolation.interp_scheme_1d(Z, yields_c13)

set_cc_yields()
set_agb_yields()
