import arya
import surp
import matplotlib.pyplot as plt
import matplotlib as mpl
import surp.gce_math as gcem
import pandas as pd
import numpy as np
import vice

from matplotlib.ticker import MultipleLocator
from mpl_toolkits.axes_grid1.inset_locator import inset_axes



import sys
sys.path.append("..")
from cc_plot_utils import plot_y_cc, plot_c11, plot_y_cc_mcmc, plot_analy, plot_c_mg_mcmc

surp.set_yields()


fig, ax = plt.subplots(figsize=(10/3, 8/3))

# Linear (left) axis)
scale = 1e4
plt.xlim(0.0, 2)
plt.ylim(1e-12, 80)

plot_y_cc(scale=scale, xscale="lin")
plot_c11(scale=scale, xscale="lin")
plot_analy(scale=scale, xscale="lin")



# final style things
lines, labs = ax.get_legend_handles_labels()

plt.ylabel(r"integrated massive-star C yield $[\times10^{-4}]$")
lab = plt.xlabel(r"$Z/Z_{\odot}$")
leg = fig.legend(lines, labs, loc='upper center', 
                 bbox_to_anchor=(0.5, -0.05), ncols=2)

# plot seperating line
box1 = leg.get_tightbbox()
box2 = lab.get_tightbbox() 
t1 = box1.transformed(fig.transFigure.inverted())
t2 = box2.transformed(fig.transFigure.inverted())
ym = (t2.y0 + t1.y1)/2

fig.add_artist(mpl.lines.Line2D([t1.x0, t1.x1], [ym, ym], color="k", lw=0.5))




plt.tight_layout()
plt.savefig("figures/lin_cc_yields.pdf")
