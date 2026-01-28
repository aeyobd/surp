import matplotlib.pyplot as plt
import arya

import sys
sys.path.append("..")
from mw_model_plots import compare_cooh, COLORS, LINESTYLES

fig, axs = plt.subplots(3, 1, figsize=(3, 6), sharex="col", sharey=True, gridspec_kw={"wspace": 0, "hspace": 0})


colors = [COLORS[0], "black", COLORS[1]]
linestyles = [":", "-", "--"]

names = [
    "fruity/zeta_lower",
    "fiducial/run",
    "fruity/zeta_higher",
]
labels = [
    r"$\zeta_{\rm C}^{\rm CC} = 0.0004$", 
    r"$\zeta_{\rm C}^{\rm CC} = 0.0008$ (fiducial)", 
    r"$\zeta_{\rm C}^{\rm CC} = 0.0012$", 
]

plt.sca(axs[0])
compare_cooh(names, labels, colors=colors, linestyles=linestyles, 
             x="FE_H", y="C_FE", use_true=False, legend=False)
arya.Legend(color_only=False, loc=2)
plt.ylim(-0.1, 0.3)
plt.xlim(-0.7, 0.4)




names = [    
    "fruity/f_0",
    "fiducial/run",
    "fruity/f_0.5",
  ]

labels = [r"$f_{\rm C}^{\rm AGB}=0$", r"$f_{\rm C}^{\rm AGB}=0.3$ (fiducial)", r"$f_{\rm C}^{\rm AGB}=0.5$",]
plt.sca(axs[1])
compare_cooh(names, labels, colors=colors, linestyles=linestyles, 
             x="FE_H", y="C_FE", use_true=False, legend=False)
arya.Legend(color_only=False, loc=2)

plt.ylim(-0.1, 0.3)
plt.xlim(-0.7, 0.4)



names = [    
    "fruity/fz_0",
    "fiducial/run",
    "fruity/fz_0.5",
  ]

labels = [r"$f_{\rm C}^{\rm AGB}=0$, $\zeta_{\rm C}^{\rm CC} = 0.0004$", r"fiducial", r"$f_{\rm C}^{\rm AGB}=0.5$, $\zeta_{\rm C}^{\rm CC} = 0.0012$",]
plt.sca(axs[2])
compare_cooh(names, labels, colors=colors, linestyles=linestyles, 
             x="FE_H", y="C_FE", use_true=False, legend=False)
arya.Legend(color_only=False, loc=2)
plt.ylim(-0.1, 0.3)
plt.xlim(-0.7, 0.4)


plt.savefig("figures/sims_zeta_f_fe.pdf")
