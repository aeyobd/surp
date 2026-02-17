import matplotlib.pyplot as plt
import arya

import sys
sys.path.append("..")
from mw_model_plots import compare_cooh, COLORS, LINESTYLES

fig, axs = plt.subplots(figsize=(10/3, 10/4))


colors = ["black", COLORS[1], COLORS[2], COLORS[3]]
linestyles = ["-", "--", ":", "-."]

names = [
    "fiducial/run",
    "fruity/f_0.5",
    "fruity/fz_0.5",
]
labels = [
    r"$f_{\rm C}^{\rm AGB}=0.25$ (fiducial)", 
    r"$f_{\rm C}^{\rm AGB}=0.5$", 
    r"$f_{\rm C}^{\rm AGB}=0.5$, steep CCSN yield", 
]

compare_cooh(names, labels, colors=colors, linestyles=linestyles, 
             x="FE_H", y="C_FE", use_true=True, legend=False)
arya.Legend(1, color_only=False, fontsize=8)
plt.ylim(-0.1, 0.2)
plt.xlim(-0.7, 0.45)


plt.savefig("figures/sims_fe.pdf")
