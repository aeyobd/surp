import matplotlib.pyplot as plt
import surp
import arya
arya.style.set_size((10/3, 10/3))

import sys
sys.path.append("..")
from mw_model_plots import find_model, compare, compare_coofe, compare_cooh, COLORS, LINESTYLES

names_agbm = [   
    "fruity/agb_mass_0.5",
    "fruity/agb_mass_0.7_constrained",
    "fiducial/run",
    "fruity/agb_mass_1.5",
    #"fruity/agb_mass_2",
  ]

labels_agbm = ["0.5", "0.7", "1", "1.5", "2"]
colors_agbm = [COLORS[0], COLORS[2], "black", COLORS[1]]
ls_agbm = [":", "--", "-", "-."]




compare_coofe(names_agbm, labels_agbm, legend=False, colors=colors_agbm, linestyles=ls_agbm)
arya.Legend(loc=1, title=r"AGB mass shift:", labelspacing=0.1, alignment="right")
plt.xticks([0.1, 0.2, 0.3])

plt.tight_layout()

plt.savefig("figures/sims_agb_mass.pdf")
