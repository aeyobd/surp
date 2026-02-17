import pandas as pd
import matplotlib.pyplot as plt
import surp

import surp.gce_math as gcem
import arya
import vice
import numpy as np

from mcmc_setup import results, yagb_props


plot_labels = {
    "fruity": r"FRUITY (fiducial)",
    "aton": r"ATON",
    "monash": r"Monash",
    "nugrid": r"NuGrid",
    "fruity_mf0.7": r"FRUITY shifted",
    #"lateburst": r"lateburst",
    "twoinfall": r"twoinfall",
    "eta2": r"doubled yields",
    "sneia_1.2": r"1.2$\times$ SN Ia",
}


colors = [*arya.COLORS[:5], *np.full(5, arya.COLORS[0])]

Nr = len(plot_labels)

def plot_dist(x, y=0, color=None, **kwargs):
    ll, l, m, h, hh = np.quantile(x, [0.02, 0.16, 0.5, 0.84, 0.98])
    plt.scatter(m, y, color=color, **kwargs)
    #plt.plot([l, h], [y, y], color=color)
    #plt.plot([ll, hh], [y, y], color=color, lw=0.5)


def plot_hists(ax, col, ylabel=True):
    for i, (key, label) in enumerate(plot_labels.items()):
        if i < 5:
            color = arya.COLORS[i]
        else:
            color = arya.COLORS[0]

        result = results[key]
        if key == "eta2" and col == "alpha":
            x = 2*result.samples[col]
        else:
            x = result.samples[col]
        plot_dist(x, color=color, y=Nr-i-1)



fig, ax = plt.subplots()

plt.axvspan(0.15, 0.3, color="k", alpha=0.1)

plot_hists(ax, "f_agb")
plt.ylim(-0.5, Nr - 0.5)
plt.yticks(np.arange(0, Nr), labels=reversed(plot_labels.values()))
plt.yticks([], minor=True)

for label, color in zip(ax.get_yticklabels(), reversed(colors[:Nr])):
    label.set_color(color)





plt.xlabel(r"$f_{\rm C}^{\rm AGB}$")
plt.xlim(-0.05, 0.5)

plt.savefig("figures/mcmc_fagb.pdf")
