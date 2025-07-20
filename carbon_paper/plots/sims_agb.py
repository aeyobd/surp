import matplotlib.pyplot as plt
import surp
import arya
arya.style.set_size((10/3, 10/3))

import sys
sys.path.append("..")
from mw_model_plots import find_model, compare, compare_coofe, compare_cooh


names = [    
    "fiducial/best",
    "aton/run",
    "monash/run",
    "nugrid/run",
   "fruity/agb_mass_0.7_alpha",
  ]

labels = ["FRUITY", "ATON", "Monash",  "NuGrid", "FRUITY shifted"]

compare(names, labels)
plt.ylim(-0.25, 0.05)
plt.savefig("figures/sims_agb.pdf")
