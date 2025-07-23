import matplotlib.pyplot as plt
import surp
import arya
arya.style.set_size((10/3, 10/3))

import sys
sys.path.append("..")
from mw_model_plots import find_model, compare, compare_coofe, compare_cooh
from mc_plot_utils import plot_samples_caah, plot_samples_caafe
from mcmc_setup import results


names = [    
    "fiducial/best",
    "aton/run",
    "monash/run",
    "nugrid/run",
   "fruity/agb_mass_0.7_alpha",
  ]

labels = ["FRUITY", "ATON", "Monash",  "NuGrid", "FRUITY shifted"]


fig, axs = plt.subplots(1, 2, figsize=(7, 3), sharex="col", sharey=True,  gridspec_kw={"wspace": 0, "hspace": 0})

compare(names, labels, axs=axs)

plt.sca(axs[0])
#plot_samples_caah(results["fruity"], color=arya.COLORS[0], alpha=0.01, skip=100)

plt.sca(axs[1])
#plot_samples_caafe(results["fruity"], color=arya.COLORS[0], alpha=0.01, skip=100)
plt.savefig("figures/sims_agb.pdf")
