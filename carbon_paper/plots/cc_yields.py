import arya
import matplotlib.pyplot as plt
import matplotlib as mpl
import surp.gce_math as gcem
import pandas as pd
import numpy as np
import vice

import sys
sys.path.append("..")
from cc_plot_utils import plot_y_cc, plot_c11, plot_y_cc_mcmc, plot_analy, plot_c_mg_mcmc, y_c_cc, y_c_cc2

fig, axs = plt.subplots(1, 2, figsize=(7, 3), gridspec_kw={"wspace": 0.3})


samples = pd.read_csv("../../models/perturbations/mc_analysis/fruity_quad/mcmc_samples.csv")

# left panel
plt.sca(axs[0])

plot_y_cc()
plot_c11()

plot_analy()
# plot AGB line
plot_y_cc_mcmc(samples)
plt.yscale("log")

plt.xlabel(r"$\log Z/Z_{\odot}$")

y_scale = 1e4
plt.ylabel(r"integrated C CCSN yield, $y_{\rm C}^{\rm CC}\quad [\times 10^{-4}]$")

plt.ylim(3e-4, 0.008)

lines, labs = axs[0].get_legend_handles_labels()

# c = np.arange(0, 0.0081, 0.001)
# plt.yticks(ticks=c, labels=np.int32(np.round(y_scale*c, 0)))



# right panel
plt.sca(axs[1])

plot_y_cc(ele2="mg")
m_h = np.linspace(-5, 1, 1000)
Z = gcem.MH_to_Z(m_h)
y_mg = vice.yields.ccsne.settings["mg"]
y = gcem.abund_ratio_to_brak([y_c_cc(z)/y_mg for z in Z], "c", "mg")
plt.plot(m_h, y, color="k")

y = gcem.abund_ratio_to_brak([y_c_cc2(z)/y_mg for z in Z], "c", "mg")
plt.plot(m_h, y, color="k", linestyle="--")
plot_c_mg_mcmc(samples)

# y = gcem.abund_ratio_to_brak([y_c_cc2(z)/y_mg for z in Z], "c", "mg")
# plt.plot(m_h, y, color="k", ls="--")




# final style things
lab = plt.xlabel(r"$\log Z/Z_{\odot}$")
plt.ylabel(r"[C/Mg]$^\text{CC}$")
plt.xlim(-4.8, 0.8)

    
leg = fig.legend(lines, labs, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncols=4)
box1 = leg.get_tightbbox()
box2 = lab.get_tightbbox() 


t1 = box1.transformed(fig.transFigure.inverted())
t2 = box2.transformed(fig.transFigure.inverted())
ym = (t2.y0 + t1.y1)/2


# plt.legend(handles =l, bbox_to_anchor=(0,-0.2), loc="upper left")
fig.add_artist(mpl.lines.Line2D([t1.x0, t1.x1], [ym, ym], color="k", lw=0.5))

plt.savefig("figures/cc_yields.pdf")
