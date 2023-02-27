import matplotlib.pyplot as plt

import sys
sys.path.append("..")

import src.analysis.plotting_utils as pluto
from src.analysis.apogee_analysis import subgiants

import plot_style

ha = subgiants["high_alpha"]

params = {
            "s": 0.5
            }

df = subgiants[~ha]
plt.scatter(df["MG_H"], df["C_MG"], label="low $\\alpha$", **params)

df = subgiants[ha]
plt.scatter(df["MG_H"], df["C_MG"], label="high $\\alpha$", zorder=2,
         **params)

pluto.fancy_legend(colors=[pluto.COLORS[0], pluto.COLORS[1]])

plt.xlim(-0.6, 0.6)
plt.ylim(-0.5, 0.2)
plt.xlabel("[Mg/H]")
plt.ylabel("[C/Mg]")

plot_style.save()
