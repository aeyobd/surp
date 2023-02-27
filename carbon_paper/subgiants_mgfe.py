import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import SubplotDivider, Size

import sys
sys.path.append("..")

from src.analysis.apogee_analysis import subgiants

import plot_style

fig, (ax, ax_cb) = plt.subplots(1, 2)

width = 3
height = width
padding = 0.1
cbar_width = 0.05 # relative
divider = SubplotDivider(fig, 111,
                         horizontal=[Size.Fixed(width),Size.Fixed(padding), Size.Fixed(width * cbar_width)],
                         vertical=[Size.Fixed(height)])

plt.sca(ax)

plt.xlim(-0.1, 0.5)
plt.ylim(-0.45, 0.15)
plt.xlabel("[Mg/Fe]")
plt.ylabel("[C/Mg]")

f = ax.scatter(subgiants["MG_FE"], subgiants["C_MG"], c=subgiants["MG_H"],
                vmin=-0.5, s=0.5)


ax.set_axes_locator(divider.new_locator(nx=0, ny=0))
ax_cb.set_axes_locator(divider.new_locator(nx=2, ny=0))

fig.colorbar(f, cax=ax_cb, label="[Mg/H]")

plot_style.save()
