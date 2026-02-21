import matplotlib.pyplot as plt
import surp
import arya
arya.style.set_size((10/3, 10/3))

import sys
sys.path.append("..")
from mw_model_plots import find_model, compare, compare_coofe, compare_cooh, COLORS, LINESTYLES

#names_fz = [   
    #"fruity/fz_0.1",
    #"fiducial/run",
    #"fruity/fz_0.5",
  #]

#labels_fz = [r"$f_{\rm C}^{\rm AGB}=0.1$", r"$f_{\rm C}^{\rm AGB}=0.3$", r"$f_{\rm C}^{\rm AGB}=0.5$",]
names_agb = [    
    "fiducial/run",
    "aton/run",
    "monash/run",
    "nugrid/run",
    "fruity/agb_mass_0.7_alpha",
  ]

labels_agb = ["FRUITY (fiducial)", "ATON", "Monash",  "NuGrid", "FRUITY shifted"]
colors_agb = ["black", *COLORS[1:]]
ls_agb = LINESTYLES


fig, ax = plt.subplots()

plt.sca(ax)
compare_coofe(names_agb, labels_agb, legend=False, colors=colors_agb, linestyles=ls_agb)
plt.xticks([0, 0.1, 0.2, 0.3])
arya.Legend(loc=3, title=r"", labelspacing=0.1)



plt.tight_layout()

plt.savefig("figures/sims_agb.pdf")
