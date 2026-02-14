import matplotlib.pyplot as plt
import arya

import sys
sys.path.append("..")
from mw_model_plots import compare, COLORS, LINESTYLES

fig, axs = plt.subplots(1, 2, sharex="col", sharey=True, gridspec_kw={"wspace": 0, "hspace": 0}, figsize=(6, 3))


colors = ["black", *COLORS]
linestyles = ["-", ":", "-.", "--", "-"]

names = [
    "fiducial/run",
    #"multi_perturbations/fiducial",
    "multi_perturbations/t_d_ia0.03",
    "multi_perturbations/ia_liam",
    "fiducial/snia_0.7",
    "multi_perturbations/mlr_vincenzo",
]
labels = [
    "fiducial",
    #"fiducial2",
    r"$t_{\rm D, min}=30\,$Myr",
    "dubay+ Ia",
    r"0.7$\times$SN Ia",
    "Vincenzo+16 MLR"
]

compare(names, labels, axs = axs, colors=colors, linestyles=linestyles)




plt.savefig("figures/sims_referee.pdf")
