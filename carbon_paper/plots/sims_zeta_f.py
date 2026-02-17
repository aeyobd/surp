import matplotlib.pyplot as plt
import arya

import sys
sys.path.append("..")
from mw_model_plots import compare, COLORS, LINESTYLES

fig, axs = plt.subplots(3, 2, figsize=(7, 7), sharex="col", sharey=True, gridspec_kw={"wspace": 0, "hspace": 0})


colors = [COLORS[0], "black", COLORS[1]]
linestyles = [":", "-", "--"]

names = [
    "fruity/zeta_lower",
    "fruity/best",
    "fruity/zeta_higher",
]
labels = [
    r"shallow CCSN yield", 
    r"fiducial", 
    r"steep CCSN yield", 
]

compare(names, labels, axs = axs[0], colors=colors, linestyles=linestyles)




names = [    
    "fruity/f_0",
    #"fiducial/run",
    "fruity/best",
    "fruity/f_0.5",
  ]

labels = [r"$f_{\rm C}^{\rm AGB}=0$", r"$f_{\rm C}^{\rm AGB}=0.3$ (fiducial)", r"$f_{\rm C}^{\rm AGB}=0.5$",]
compare(names, labels, colors=colors, linestyles=linestyles, axs=axs[1])



names = [    
    "fruity/fz_0",
    #"fiducial/run",
    "fruity/best",
    "fruity/fz_0.5",
  ]

labels = [r"$f_{\rm C}^{\rm AGB}=0$, shallow CCSN yield", r"fiducial", r"$f_{\rm C}^{\rm AGB}=0.5$, steep CCSN yield",]
compare(names, labels, colors=colors, linestyles=linestyles, axs=axs[2])


plt.savefig("figures/sims_zeta_f.pdf")
