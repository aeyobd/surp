import arya
import surp
import matplotlib.pyplot as plt
import matplotlib as mpl
import surp.gce_math as gcem
import pandas as pd
import numpy as np
import vice

from matplotlib.ticker import MultipleLocator


import sys
sys.path.append("..")
from cc_plot_utils import plot_y_cc, plot_c11, plot_y_cc_mcmc, plot_analy, plot_c_mg_mcmc

surp.set_yields()

# functions for secondary axis
scale = 1e4

ymg = vice.yields.ccsne.settings["mg"]

def linear_to_log10(y):
    return gcem.abund_ratio_to_brak(y / ymg / scale, "c", "mg")

def log10_to_linear(c_mg):
    return gcem.brak_to_abund_ratio(c_mg, "c", "mg") * ymg * scale


fig, ax = plt.subplots(figsize=(10/3, 8/3))

plot_y_cc(scale=scale)
plot_c11(scale=scale)
plot_analy(scale=scale)

plt.ylabel(r"integrated massive-star C yield $[\times10^{-4}]$")
plt.xlim(-4.8, 0.8)
plt.ylim(1e-12, 80)

# add secondary axis
ax2 = ax.secondary_yaxis('right', functions=(linear_to_log10, log10_to_linear))
ax2.set_ylabel(r"${\rm [C/Mg]}^{\rm CC}$", rotation=-90)
ax2.set_yticks([-2.3, -2, -1.6, -1.3, -1, -0.6, -0.3, 0.0, 0.3], labels=["", "", "", "", -1, -0.6, -0.3, 0, 0.3])
ax2.yaxis.set_minor_locator(MultipleLocator(0.1))
ax.tick_params(axis="y", which="both", right=False, left=True)


# final style things
lines, labs = ax.get_legend_handles_labels()

lab = plt.xlabel(r"$\log Z/Z_{\odot}$")
leg = fig.legend(lines, labs, loc='upper center', 
                 bbox_to_anchor=(0.5, -0.05), ncols=2)

# plot seperating line
box1 = leg.get_tightbbox()
box2 = lab.get_tightbbox() 
t1 = box1.transformed(fig.transFigure.inverted())
t2 = box2.transformed(fig.transFigure.inverted())
ym = (t2.y0 + t1.y1)/2

fig.add_artist(mpl.lines.Line2D([t1.x0, t1.x1], [ym, ym], color="k", lw=0.5))

# finalize and save
plt.tight_layout()
plt.savefig("figures/cc_yields.pdf")
