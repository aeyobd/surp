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

fig, ax = plot_style.get_plot()

df = subgiants[~ha]
ax.scatter(df["MG_H"], df["C_MG"], label="low $\\alpha$", **params)

df = subgiants[ha]
ax.scatter(df["MG_H"], df["C_MG"], label="high $\\alpha$", zorder=2,
         **params)

pluto.fancy_legend(ax=ax, colors=[pluto.COLORS[0], pluto.COLORS[1]])

ax.set_xlim(-0.6, 0.6)
ax.set_ylim(-0.5, 0.2)
ax.set_xlabel("[Mg/H]")
ax.set_ylabel("[C/Mg]")

plot_style.save()
