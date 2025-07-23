import matplotlib.pyplot as plt
import arya
arya.style.set_size((10/3, 10/3))

import sys
sys.path.append("..")
from mw_model_plots import compare

fig, axs = plt.subplots(2, 2, figsize=(7, 5), sharex="col", sharey=True, gridspec_kw={"wspace": 0, "hspace": 0})


names = [
    "fruity/zeta_lower",
    "fiducial/run",
    "fruity/zeta_higher",
]
labels = [
    r"shallower CC yield", 
    r"fiducial", 
    r"steeper CC yield"
]

compare(names, labels, axs = axs[0], sequential=True)




names = [    
    "fruity/f_0.1",
    "fiducial/run",
    "fruity/f_0.5",
  ]

labels = [r"$f_{\rm C}^{\rm AGB}=0.1$", r"$f_{\rm C}^{\rm AGB}=0.3$", r"$f_{\rm C}^{\rm AGB}=0.5$",]
compare(names, labels, sequential=True, axs=axs[1])


plt.savefig("figures/sims_zeta_f.pdf")
