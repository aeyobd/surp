import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import scipy

import vice

import arya
import surp
from surp._globals import AGB_MODELS
from surp import yields
from surp.yields import calc_y
from surp.gce_math import Z_SUN, MH_to_Z, Z_to_MH

from singlezone import run_singlezone


surp.set_yields()
y_agb = vice.yields.agb.settings
agb_grid = vice.yields.agb.grid
agb_interpolator = surp.agb_interpolator.interpolator

AGB_LABELS = {
    "cristallo11": "FRUITY",
    "ventura13": "ATON", 
    "karakas16": "Monash",  
    "battino19": "NuGrid"
}


Z_max = 0.04
Z_min = 0.0001

hmap = arya.HueMap((Z_to_MH(Z_min),Z_to_MH(Z_max)))


def plot_yield_table(study = "cristallo11", hmap=hmap, ele="c", fmt="o", 
                     ax=None, fig=None, factor=1, **kwargs):
    """
    Plots the yield table in VICE (without modification) for each metallicity
    """
    
    if ax is None:
        ax = plt.gca()
        ylabel = r"$Y_{\rm C}^{\rm AGB}$"
        if factor != 1:
            ylabel += r"$\quad [\times 10^{-%i}]$" % np.log10(factor)
        ax.set(xlabel=r'Mass / ${\rm M}_\odot$', ylabel=ylabel )
        
    yields, masses, Zs = agb_grid(ele, study=study)
    N = len(Zs)
    y_agb = surp.agb_interpolator.interpolator("c", study=study)

    for i in range(N):
        y = np.array(yields)[:,i] * factor
        Z = Zs[i]
        assert Z >= Z_min and Z <= Z_max
        c = hmap(Z_to_MH(Z))
        f = ax.plot(masses, y, fmt, label=f"Z = {Z}", c=c, **kwargs)

        x = np.linspace(1, 8, 1000)
        
        y = [y_agb(m, Z) * factor for m in x]
        ax.plot(x, y, c=c, **kwargs)
        
    ax.axhline(0, color="k", ls=":", zorder=-1)

    return f


def plot_yields(study = "cristallo11", masses=np.linspace(0.08, 8.01, 1000), Zs=None, ele="c", 
                ax=None, fig=None, hmap=hmap, factor=1, **kwargs):
    """
    Plots the yields (assuming the current setting is a surp.agb_interpolator)
    for each given mass and metallicity.
    
    """
    
    if ax is None:
        ax = plt.gca()
        ylabel = r"$Y_{\rm C}^{\rm AGB}$"
        if factor != 1:
            ylabel += r"$\quad [\times 10^{-%i}]$" % np.log10(factor)
        ax.set(xlabel=r'Mass / ${\rm M}_\odot$', ylabel=ylabel )


    if Zs is None:
        _yields, _masses, Zs = agb_grid(ele, study=y_agb[ele].study)
    
    ya = y_agb[ele]
    for i in range(len(Zs)):
        Z = Zs[i] 
        c = hmap(Z_to_MH(Z))
        y = [ya(m, Z)*factor for m in masses]
        f = ax.plot(masses, y, label=f"Z = {Z}", c=c, **kwargs)

    return f


def plot_y_z(Zs=MH_to_Z(np.linspace(-2.7, 0.6, 100)), ele="c", kind="agb", fmt="-", factor = 1e4, **kwargs):
    """
        plot_y_z(Zs, ele, kind, fmt, factor, kwargs)
    
    plots the metallicity dependence of the AGB yield over a given range of metallicities. 
    Uses the current yield setting
    """
    
    y_c_agb = calc_y(Zs, ele=ele, kind=kind) * factor
    
    plt.axhline(0, color="k", ls=":")
    plt.xlabel(r"$\log Z/Z_\odot$")
    plt.ylabel(r"$y_{\rm C}^{\rm AGB}\quad[\times 10^{-%i}]$" % np.log10(factor))
    
    return plt.plot(Z_to_MH(Zs), y_c_agb, fmt, **kwargs), y_c_agb


tau_switch = 1
def plot_ssp_time(ele="c", Z=surp.Z_SUN, imf="kroupa", normalize=True, dt=0.01, t_end=10, color=None, verbose=True, **kwargs):
    """
        plot_ssp_time(ele, Z, normalize, **kwargs(
        
    plots the SSP yield over time for the current yield setting
    """
    
    m_c, times = vice.single_stellar_population(ele, Z=Z, dt=dt, time=t_end, mstar=1, IMF=imf)
    
    y = np.array(m_c)
    if normalize:
        y /= y[-1]
    
    plt.plot(times, y, color=color, **kwargs)
    
    
    # plot 50% time
    f = scipy.interpolate.interp1d(y, times)

    y_1_2 = 0.5*y[-1]
    plt.scatter(f(y_1_2), y_1_2, color=color)
        
    if verbose:
        print(f"model = {y_agb[ele]}")
        print(f"t1/2 = {f(y_1_2):0.2f}")

        times = np.array(times)
        idx = np.where(times >= tau_switch)[0][1]

        y_late = y[-1] - y[idx]
        print(f"y(t>{times[idx]}) = {y_late:0.2f}")
        print(f"y max = {np.max(y):0.2f}")
        print(f"y min = {np.min(y):0.2f}")
        print(f"t min = {times[np.argmin(y)]:0.2f}")
   
        print()
    
    plt.xlabel(r"$t$ / Gyr")
    plt.xscale("log")
    
    if normalize:
        plt.ylabel(r"$y_{\rm C}^{\rm AGB}(t)\;/\;y_{\rm C}^{\rm AGB}(t_{\rm end})$")
    else:
        plt.ylabel(r"$y_{\rm C}^{\rm AGB}(t)$")

    
    return times, y
