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


fig, ax = plt.subplots(figsize=(10/3, 10/3))

# Linear (left) axis)
scale = 1e4

plot_y_cc(scale=scale, xscale="lin")
plot_c11(scale=scale, xscale="lin")
plot_analy(scale=scale, xscale="lin")

plt.xlim(0.0, 0.065)
plt.ylim(1e-12, 80)

plt.xlabel(r"$Z$")
plt.ylabel(r"integrated massive-star C yield $[\times10^{-4}]$")

#handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(loc="upper right", frameon=True, fancybox=False, framealpha=0.8, edgecolor="black")



plt.tight_layout()
plt.savefig("figures/lin_cc_yields.pdf")
