import arya
import surp
import matplotlib.pyplot as plt
import matplotlib as mpl
import surp.gce_math as gcem
import pandas as pd
import numpy as np
import vice

import sys
sys.path.append("..")
from cc_plot_utils import plot_y_cc, plot_c11, plot_y_cc_mcmc, plot_analy, plot_c_mg_mcmc

fig, ax = plt.subplots()

samples = pd.read_csv("../../models/mcmc_models_2d/fiducial/mcmc_samples.csv")

plot_y_cc()
plot_c11()

plot_analy()
#plot_y_cc_mcmc(samples)


plt.ylabel(r"integrated CCSN C yield")

plt.ylim(0.000001, 0.008)

# add secondary axis
ymg = vice.yields.ccsne.settings["mg"]
surp.set_yields()

def linear_to_log10(y):
    return gcem.abund_ratio_to_brak(y / ymg, "c", "mg")

def log10_to_linear(c_mg):
    return gcem.brak_to_abund_ratio(c_mg, "c", "mg") * ymg

# Add secondary y-axis with transform
ax2 = ax.secondary_yaxis('right', functions=(linear_to_log10, log10_to_linear))
ax2.set_ylabel(r"${\rm [C/Mg]}^{\rm CC}$")
ax2.set_yticklabels([-1, -0.5, 0.0])
ax.tick_params(axis="y", which="both", right=False, left=True)



lines, labs = ax.get_legend_handles_labels()

# final style things
plt.xlim(-4.8, 0.8)

lab = plt.xlabel(r"$\log Z/Z_{\odot}$")
leg = fig.legend(lines, labs, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncols=2)


# plot seperating line
box1 = leg.get_tightbbox()
box2 = lab.get_tightbbox() 
t1 = box1.transformed(fig.transFigure.inverted())
t2 = box2.transformed(fig.transFigure.inverted())
ym = (t2.y0 + t1.y1)/2

fig.add_artist(mpl.lines.Line2D([t1.x0, t1.x1], [ym, ym], color="k", lw=0.5))

plt.tight_layout()

plt.savefig("figures/cc_yields.pdf")
