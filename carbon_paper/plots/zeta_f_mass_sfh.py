import matplotlib.pyplot as plt
import surp
import arya
arya.style.set_size((10/3, 10/3))

import sys
sys.path.append("..")
from mw_model_plots import find_model, compare, compare_coofe, compare_cooh

names_fz = [   
    "fruity/fz_0.1",
    "fiducial/run",
    "fruity/fz_0.5",
  ]

labels_fz = [r"$f_{\rm C}^{\rm AGB}=0.1$", r"$f_{\rm C}^{\rm AGB}=0.3$", r"$f_{\rm C}^{\rm AGB}=0.5$",]


names_agbm = [   
    "fruity/agb_mass_0.5",
    "fruity/agb_mass_0.7",
    "fiducial/run",
    "fruity/agb_mass_1.5",
    #"fruity/agb_mass_2",
  ]

labels_agbm = ["0.5", "0.7", "1", "1.5", "2"]


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
    r"$y\rightarrow 2y$",
]


fig, axs = plt.subplots(1, 3, figsize=(7, 2.5), sharex="col", sharey=True, gridspec_kw={"wspace": 0, "hspace": 0})

plt.sca(axs[0])
compare_coofe(names_fz, labels_fz, sequential=True, legend=False)
arya.Legend(loc=1, color_only=True, title=r"Free CC:", labelspacing=0.1)

plt.sca(axs[1])
compare_coofe(names_agbm, labels_agbm, sequential=True, legend=False)
arya.Legend(loc=1, color_only=True, title=r"AGB mass shift:", labelspacing=0.1)
plt.ylabel("")

plt.sca(axs[2])
compare_coofe(names_sfh, labels_sfh)
plt.ylabel("")

plt.tight_layout()

plt.savefig("figures/zeta_f_mass_sfh.pdf")
