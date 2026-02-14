import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

import arya

import vice
import surp
from surp.gce_math import MH_to_Z, Z_to_MH
from surp.agb_interpolator import interpolator as agb_interpolator

import sys
sys.path.append("..")
from yield_plot_utils import AGB_MODELS, AGB_LABELS, plot_yield_table, hmap, plot_y_z, plot_ssp_time


def plot_y_agb(fig, ax):
    SCALE_FACTOR=1e2

    study = AGB_MODELS[0]
    label = AGB_LABELS[study]
    f = plot_yield_table(study, ax=ax, 
                         fig=fig, fmt="o", factor=SCALE_FACTOR)
    
    # plot label
    plt.annotate(xy=(0,0), xytext=(8,8), 
                 text="FRUITY",
                 xycoords="axes fraction", textcoords="offset points",
                 horizontalalignment='left',
                verticalalignment='bottom')
        

    handles, labels = plt.gca().get_legend_handles_labels()
    arya.Legend(handles=handles[::2], labels=labels[::2], color_only=True, fontsize=8)



    plt.xlabel(r'initial mass / ${\rm M}_\odot$')
    plt.ylabel(r"stellar C yield $\quad[\times 10^{-2}]$")

    plt.gca().xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))




def plot_y_agb_vs_t():
    vice.yields.ccsne.settings["c"] = 0
    vice.yields.sneia.settings["c"] = 0
    vice.yields.ccsne.settings["fe"] = 0
    vice.yields.agb.settings["fe"] = surp.yield_models.ZeroAGB()

    for i in range(4):
        model = AGB_MODELS[i]
        vice.yields.agb.settings["c"] = agb_interpolator("c", study=model)
        times, y = plot_ssp_time(Z=surp.gce_math.MH_to_Z(-0.1), label=AGB_LABELS[model])
      
        
    plt.text(3, 0.7, "SNe Ia Fe", rotation=42, color="k")
    plot_ssp_time("fe", color="k", ls="--", zorder=-1)

    plt.ylim(-0.3, 1.2)
    plt.xlim(0.03, 13.2)
    plt.xticks([0.1, 1, 10], labels=[0.1, 1, 10])
    plt.ylabel("cumulative AGB C production")
    plt.xlabel("time / Gyr")
    arya.Legend(color_only=True, loc=0, fontsize=8)


def plot_y_agb_vs_z():
    x_min = -2.8
    x_max = 0.6
    N_points = 100
    scale = 1e4
    ele = "c"

    vice.yields.ccsne.settings[ele] = 0
    vice.yields.sneia.settings[ele] = 0

    for i in range(4):
        model = AGB_MODELS[i]

        vice.yields.agb.settings[ele] = agb_interpolator(ele, study=model)
        kwargs = dict(fmt="o", zorder=i, factor=scale, color=arya.COLORS[i])
        
        # plots importaint points
        _y1, _m1, Zs = vice.yields.agb.grid('c', study=model)
        (line,), _x = plot_y_z(Zs, **kwargs)
        
        # plot solid within range
        MoverH_min = Z_to_MH(min(Zs))
        MoverH_max = Z_to_MH(max(Zs))
        
        kwargs["fmt"] = "-"
        Zs = MH_to_Z(np.linspace(MoverH_min, MoverH_max, N_points))
        plot_y_z(Zs, label=AGB_LABELS[model], **kwargs)

        # dashed extrapolation
        kwargs["fmt"] = "--"
        Zs = MH_to_Z(np.linspace(x_min, MoverH_min, N_points))    
        plot_y_z(Zs, **kwargs)
        Zs = MH_to_Z(np.linspace(MoverH_max, x_max, N_points))
        plot_y_z(Zs, **kwargs)



    arya.Legend(color_only=True, handlelength=0, ncols=2, columnspacing=1, loc=3, transpose=True, fontsize=8)
    plt.ylabel(r"integrated AGB C yield $\quad [\times 10^{-4}]$")


def main():
    fig, axs = plt.subplots(1, 3, figsize=(7, 2.5))

    plt.sca(axs[0])
    plot_y_agb(fig, axs[0])

    plt.sca(axs[1])
    plot_y_agb_vs_z()

    plt.sca(axs[2])
    plot_y_agb_vs_t()

    plt.tight_layout()
    plt.savefig("figures/y_agb_threepanel.pdf")


if __name__ == "__main__":
    main()
