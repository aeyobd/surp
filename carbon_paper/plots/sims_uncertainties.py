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
    "fruity/best",
    "aton/run",
    "monash/run",
    "nugrid/run",
   "fruity/agb_mass_0.7_alpha",
  ]

labels_agb = ["fiducial", "FRUITY", "ATON", "Monash",  "NuGrid", "FRUITY shifted"]
colors_agb = ["black", *COLORS]
ls_agb = ["-", *LINESTYLES]


names_agbm = [   
    "fruity/agb_mass_0.5",
    "fruity/agb_mass_0.7_fixed",
    "fiducial/run",
    "fruity/agb_mass_1.5",
    #"fruity/agb_mass_2",
  ]

labels_agbm = ["0.5", "0.7", "1", "1.5", "2"]
colors_agbm = [COLORS[0], COLORS[2], "black", COLORS[1]]
ls_agbm = ["-.", "--", "-", ":"]


names_sfh = [
    "fiducial/run",
    "fiducial/twoinfall",
    "fiducial/lateburst",
    "fiducial/eta2",
]
labels_sfh = [
    r"fiducial",  
    r"twoinfall",
    "lateburst",
    r"doubled yields/$\eta$",
]
colors_sfh = ["black", *COLORS]
ls_sfh = ["-", *LINESTYLES]


fig, axs = plt.subplots(1, 3, figsize=(7, 2.5), sharex="col", sharey=True, gridspec_kw={"wspace": 0, "hspace": 0})

plt.sca(axs[0])
compare_coofe(names_agb, labels_agb, legend=False, colors=colors_agb, linestyles=ls_agb)
plt.xticks([0, 0.1, 0.2, 0.3])
arya.Legend(loc=3, title=r"", labelspacing=0.1)

plt.sca(axs[1])
compare_coofe(names_agbm, labels_agbm, legend=False, colors=colors_agbm, linestyles=ls_agbm)
arya.Legend(loc=1, title=r"AGB mass shift:", labelspacing=0.1, alignment="right")
plt.xticks([0.1, 0.2, 0.3])
plt.ylabel("")

plt.sca(axs[2])
compare_coofe(names_sfh, labels_sfh, legend=False, colors=colors_sfh, linestyles=ls_sfh)
plt.xticks([0.1, 0.2, 0.3, 0.4])
arya.Legend(loc=3, labelspacing=0.1)
plt.ylabel("")

plt.tight_layout()

plt.savefig("figures/zeta_f_mass_sfh.pdf")
