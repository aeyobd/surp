import pandas as pd
import matplotlib.pyplot as plt
import surp

import surp.gce_math as gcem
import arya
import vice
import numpy as np

from mcmc_setup import results, yagb_props



Y_C_0 = 2.67e-3

plot_labels = {
    #"fiducial": r"FRUITY+gas-phase",
    "fruity": r"FRUITY",
    "aton": r"ATON",
    "monash": r"Monash",
    "nugrid": r"NuGrid",
    "fruity_mf0.7": r"FRUITY shifted",
    "lateburst": r"lateburst",
    "twoinfall": r"twoinfall",
    "eta2": r"eta2",
    "sneia_1.2": r"$1.2 \times y_{\rm Fe}^{\rm Ia}$"
}


def plot_hists(axs, col, ylabel=True):
    for i, (key, label) in enumerate(plot_labels.items()):
        if key == "hline":
            ax = axs[i]
            plt.sca(axs[i])
            ax.spines[['bottom', 'top']].set_visible(False)
            plt.axhline(0.5, color=label, linestyle=":")
            ax.xaxis.set_visible(False)
            ax.set_yticks([])
            ax.set_yticks([], minor=True)
            
            continue

        if i < 5:
            color = arya.COLORS[i]
            ls = "-"
        else:
            ls = "--"
            color = arya.COLORS[0]

        result = results[key]
        ax = axs[i]
        plt.sca(axs[i])
        if key == "eta2" and col == "alpha":
            plt.hist(2*result.samples[col], color=color, ls=ls, density=True)
        else:
            plt.hist(result.samples[col], color=color, ls=ls, density=True)

        # add wider histogram
        if key not in ["lateburst", "twoinfall", "eta2", "sneia_1.2"]:
            result2 = results[key + "_sigma"]
            plt.hist(result2.samples[col], color=color, histtype="step", density=True, ls="-", lw=0.5)
        if ylabel:
            plt.ylabel(label, rotation=0, ha="right", va="center")

        if key in yagb_props.keys():
            y_a = yagb_props[key]["y0"]
        elif key == "fruity_m0.7":
            y_a = yagb_props["fruity_mf0.7"]["y0"]
        else:
            print(f"warning, {key} not found")
            y_a = yagb_props["fruity"]["y0"]

        f0 = y_a / Y_C_0
        print("f = ", f0, " key, ", key)

        if Nr - 1 > i > 0:
            ax.spines[['bottom', 'top']].set_visible(False)
            ax.xaxis.set_visible(False)
        elif i == 0:
            ax.spines[['bottom']].set_visible(False)
            ax.tick_params(axis='x',  bottom=False, which="both")
        elif i == Nr - 1:
            ax.spines[['top']].set_visible(False)
            ax.tick_params(axis='x',  top=False, which="both")


        ax.set_yticks([])
        ax.set_yticks([], minor=True)
        #plt.ylim(-0.1)





Nr = len(plot_labels)
fig, axs = plt.subplots(Nr, 2, figsize=(12/3, 10/4), sharex="col", gridspec_kw={"hspace": 0})

plot_hists(axs[:, 0], "f_agb")
plot_hists(axs[:, 1], "alpha", ylabel=False)


for ax in axs[:, 1]:
    ax.axvline(1, color="black")


f0 = 0.3
axs[0, 0].annotate("", (f0, 0), xytext=(0, 0.5), textcoords="offset fontsize", arrowprops={"width": 0.5, "headwidth": 3, "headlength": 3, "color": "k", "linewidth": 0.0, "edgecolor": "black"})
f0 = 2.47
axs[0, 1].annotate("", (f0, 0), xytext=(0, 0.5), textcoords="offset fontsize", arrowprops={"width": 0.5, "headwidth": 3, "headlength": 3, "color": "k", "linewidth": 0.0, "edgecolor": "black"})

plt.sca(axs[-1, 0])
plt.xlabel(r"$f_{\rm C}^{\rm AGB}$")
plt.xlim(-0.05, 0.6)

plt.sca(axs[-1, 1])
plt.xlabel(r"$\beta_{\rm C}^{\rm AGB}$")
plt.xlim(0, 4)
#plt.tight_layout()
plt.savefig("figures/mcmc_fagb.pdf")
