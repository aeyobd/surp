import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd

import vice
import os

from surp import gce_math as gcem
from surp._globals import AGB_MODELS
from surp import subgiants
import surp
import arya


ALLOWED_MH = {
    "LC18": [-3, -2, -1, 0],
    "S16/N20": [0],
    "S16/W18": [0],
    "S16/W18F": [0],
    "CL13": [0],
    "NKT13": [-np.inf, -1.15, -0.54, -0.24, 0.15, 0.55],
    "CL04": [-np.inf, -4, -2, -1, -0.37, 0.15],
    "WW95": [-np.inf, -4, -2, -1, 0]
    }

MAX_MASS = {
    "LC18": 120,
    "S16/N20": 120,
    "S16/W18": 120,
    "S16/W18F": 120,
    "NKT13": 40,
    "WW95": 40,
    "CL04": 35,
    "CL13": 120,
}



Y_CONST_MCMC = lambda z: 1e-3
Y_LIN_MCMC = np.vectorize(lambda z: surp.yield_models.Lin_CC(y0=0.001, slope=0.001/surp.Z_SUN)(z))

def load_fiducial():
    current_dir = os.path.dirname(os.path.realpath(__file__)) + "/"
    surp.yields.set_yields(surp.YieldParams.from_file(current_dir + "../models/fiducial/yield_params.toml"), verbose=False)
    y_c_cc = vice.yields.ccsne.settings["c"]
    return y_c_cc

Y_C_CC_FIDUCIAL = load_fiducial()


def plot_y_cc(ele='c', ele2=None,
        ccsne_studies = ["LC18", "LC18", "S16/W18F", "S16/W18", "NKT13", "WW95"],
        colors = [arya.style.COLORS[i] for i in [0,0,1,1,2,3,4]],
        markers = ["o", "o", "s", "d", "*", "^"],
        sizes = [30, 30,30, 30,30,30],
        rotations = [0, 300, 0, 0, 0, 0],
        scale = 1
              ):

    labels = [r"LC18, $v_{\rm rot}=0\;{\rm km\,s^{-1}}$", 
              r"LC18, $v_{\rm rot}=300\;{\rm km\,s^{-1}}$",
              "S16/All explode", 
              "S16/W18", 
              "NKT13", 
              "WW95"]


    N = len(ccsne_studies)

    for i in range(N):
        study = ccsne_studies[i]
        metalicities = ALLOWED_MH[study]
        m_upper = MAX_MASS[study]
        rotation = rotations[i]

        y = [vice.yields.ccsne.fractional(ele, study=study, MoverH=metalicity, 
            rotation=rotation, m_upper=m_upper)[0]
             for metalicity in metalicities]
        if ele2 is not None:
            y2 = np.array([vice.yields.ccsne.fractional(ele2, study=study, MoverH=metalicity, 
                rotation=rotation, m_upper=m_upper)[0]
                 for metalicity in metalicities])
            y = np.log10(y/y2) - np.log10(vice.solar_z(ele)/vice.solar_z(ele2))

        marker = markers[i]
        color = facecolor = colors[i]
        label = labels[i]

        # handle 0 metallicity stars by plotting at -4.5
        if np.isinf(metalicities[0]):
            if study == "WW95":
                x0 = -4.5
                ms = 5
                zorder = 2
            else:
                x0 = -4.5
                ms = 6
                zorder = 3
            plt.errorbar(x0, y[0] * scale, xerr=[0.2], fmt=marker, color=color, 
                         xuplims=[1],ms=ms, zorder=zorder, capsize=0)

            # remove problematic point
            x = metalicities[1:]
            y = y[1:]
        else:
            x = metalicities

        # rotation is transparent
        if rotation == 150:
            facecolor=(1,1,1,0)
        if rotation == 300:
            facecolor=(1,1,1,0)

        # plot the points
        plt.scatter(x, [yy * scale for yy in y], 
                ec=color, label=label, lw=1, fc=facecolor, 
                    marker=marker, s=sizes[i])




def plot_y_cc_mcmc(samples, thin=100, M_H=np.linspace(-0.5, 0.5, 1000), color="black", alpha=None):
    Z = gcem.MH_to_Z(M_H)
    if alpha is None:
        alpha = 1 / (len(samples)/thin)**(1/3) / 10
        
    ys_z0 = Y_CONST_MCMC(Z)
    ys_z1 = Y_LIN_MCMC(Z)
    #ys_z2 = y_z2(Z)
    ymg = vice.yields.ccsne.settings["mg"]

    for i, sample in samples[::thin].iterrows():
        yt = sample.y0_cc * ys_z0 + sample.zeta_cc * ys_z1 #+ sample.A_cc * ys_z2 
        plt.plot(M_H, yt , color=color, alpha=alpha, rasterized=False)
    

def plot_c_mg_mcmc(samples, thin=100, M_H=np.linspace(-0.5, 0.5, 1000), color="black", alpha=None):
    Z = gcem.MH_to_Z(M_H)
    if alpha is None:
        alpha = 1 / (len(samples)/thin)**(1/3) / 10
        
    ys_z0 = Y_CONST_MCMC(Z)
    ys_z1 = Y_LIN_MCMC(Z)
    #ys_z2 = y_z2(Z)
    ymg = vice.yields.ccsne.settings["mg"]

    for i, sample in samples[::thin].iterrows():
        yt = sample.y0_cc * ys_z0 + sample.zeta_cc * ys_z1 #+ sample.A_cc * ys_z2 
        plt.plot(M_H, gcem.abund_ratio_to_brak(yt / ymg, "c", "mg"), color=color, alpha=alpha, rasterized=False)




def plot_analy(scale = 1):
    """Plot fiducial C CC yield"""
    m_h = np.linspace(-5, 1, 1000)
    Z = gcem.MH_to_Z(m_h)
    plt.plot(m_h, [Y_C_CC_FIDUCIAL(z) * scale for z in Z], color="k", ls="-", zorder=-2, label="Adopted")

    

def plot_c11(scale=1):
    """Plot the cristallo ++ yield with metallicity"""

    vice.yields.agb.settings["c"] = surp.agb_interpolator.interpolator("c", study="cristallo11")
    vice.yields.ccsne.settings["c"] = 0
    
    # retrieve mass range
    y, m, z = vice.yields.agb.grid("c")
    mh_min = gcem.Z_to_MH(np.min(z))
    mh_max = gcem.Z_to_MH(np.max(z))

    # calc yields
    MH = np.linspace(mh_min, mh_max, 1000)
    Zs = gcem.MH_to_Z(MH)
    ys = surp.yields.calc_y(Zs, ele="c", kind="agb")
        
    plt.plot(MH, ys * scale, label="Fruity (AGB)", color=arya.COLORS[4])
    
