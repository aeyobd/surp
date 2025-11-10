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
    "fiducial": r"fiducial",
    "fruity": r"FRUITY",
    "aton": r"ATON",
    "monash": r"Monash",
    "nugrid": r"NuGrid",
    "fruity_mf0.7": r"FRUITY shifted",
    "lateburst": r"lateburst",
    "twoinfall": r"twoinfall",
    "eta2": r"doubled yields",
    "sneia_1.2": r"higher SN Ia"
}


def plot_dist(x, y=1, color=None, **kwargs):
    ll, l, m, h, hh = np.quantile(x, [0.02, 0.16, 0.5, 0.84, 0.98])
    plt.scatter(m, y, color=color, **kwargs)
    plt.plot([l, h], [y, y], color=color)
    plt.plot([ll, hh], [y, y], color=color, lw=0.5)


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

        if i == 0:
            color = "black"
        elif i < 6:
            color = arya.COLORS[i-1]
        else:
            color = arya.COLORS[0]
        
        ax = axs[i]
        plt.sca(axs[i])

        if key == "fiducial":
            if col == "f_agb":
                plt.scatter(0.3, 0, color="black")
            else:
                plt.scatter(2.47, 0, color="black")
        else:
            result = results[key]
            if key == "eta2" and col == "alpha":
                x = 2*result.samples[col]
            else:
                x = result.samples[col]
                #plt.hist(2*result.samples[col], color=color, ls=ls, density=True)
            plot_dist(x, color=color)

        # add wider histogram
        if key not in ["fiducial", "lateburst", "twoinfall", "eta2", "sneia_1.2"]:
            result2 = results[key + "_sigma"]
            #plt.hist(result2.samples[col], color=color, histtype="step", density=True, ls="-", lw=0.5)
            plot_dist(result2.samples[col], marker="^", color=color, y=-1)
        if ylabel:
            plt.ylabel(label, rotation=0, ha="right", va="center", color=color)

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


        ax.set_yticks([0])
        ax.axes.yaxis.set_ticklabels([])
        ax.set_yticks([], minor=True)
        plt.ylim(-4, 4)





Nr = len(plot_labels)
fig, axs = plt.subplots(Nr, 2, figsize=(11.5/3, 10/4), sharex="col", gridspec_kw={"hspace": 0, "wspace": 0})

plot_hists(axs[:, 0], "f_agb")
plot_hists(axs[:, 1], "alpha", ylabel=False)


for ax in axs[:, 1]:
    ax.axvline(1, color="black", linewidth=0.5)



plt.sca(axs[-1, 0])
plt.xlabel(r"$f_{\rm C}^{\rm AGB}$")
plt.xlim(-0.05, 0.55)

plt.sca(axs[-1, 1])
plt.xlabel(r"$\beta_{\rm C}^{\rm AGB}$")
plt.xlim(0, 4)
#plt.tight_layout()
plt.savefig("figures/mcmc_fagb.pdf")
