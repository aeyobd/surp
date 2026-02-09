import matplotlib.pyplot as plt
import arya

import sys
sys.path.append("..")
from mw_model_plots import compare_cooh, COLORS, LINESTYLES

fig, axs = plt.subplots()


colors = ["black", COLORS[1], COLORS[2], COLORS[3]]
linestyles = ["-", "--", ":", "-."]

names = [
    "fiducial/run",
    #"fruity/zeta_higher",
    "fruity/f_0.5",
    "fruity/fz_0.5",
]
labels = [
    r"$f_{\rm C}^{\rm AGB}=0.3, \zeta_{\rm C}^{\rm CC} = 0.0008$ (fiducial)", 
    #r"$f_{\rm C}^{\rm AGB}=0.3, \zeta_{\rm C}^{\rm CC} = 0.0012$", 
    r"$f_{\rm C}^{\rm AGB}=0.5, \zeta_{\rm C}^{\rm CC} = 0.008$", 
    r"$f_{\rm C}^{\rm AGB}=0.5, \zeta_{\rm C}^{\rm CC} = 0.0012$", 
]

compare_cooh(names, labels, colors=colors, linestyles=linestyles, 
             x="FE_H", y="C_FE", use_true=False, legend=False)
arya.Legend(color_only=False, loc=2)
plt.ylim(-0.1, 0.3)
plt.xlim(-0.7, 0.4)


plt.savefig("figures/sims_fe.pdf")
