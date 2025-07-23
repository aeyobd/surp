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
    "fiducial": r"FRUITY+gas-phase",
    "fruity": r"FRUITY",
    "aton": r"ATON",
    "monash": r"Monash",
    "nugrid": r"NuGrid",
    "fruity_mf0.7": r"FRUITY m0.7",
}



Nr = len(plot_labels)
fig, axs = plt.subplots(Nr, 1, figsize=(3, 2), sharex="col", gridspec_kw={"hspace": 0})

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
    plt.hist(result.samples.f_agb, color=color, ls=ls)
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
    #plt.scatter(f0, 0, c="black", marker="o", s=5)
    plt.scatter(f0, 0, c=color, marker="o", s=3, lw=0.5, edgecolors="black")

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
    plt.ylim(-1000)



plt.sca(axs[-1])
plt.xlabel(r"$f_{\rm AGB}$")
plt.xlim(-0.05, 0.6)

plt.tight_layout()
plt.savefig("figures/mcmc_fagb.pdf")
