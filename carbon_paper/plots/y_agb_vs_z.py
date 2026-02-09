import arya
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import vice
from surp.gce_math import MH_to_Z, Z_to_MH
from surp.agb_interpolator import interpolator as agb_interpolator

import sys
sys.path.append("..")
from yield_plot_utils import AGB_MODELS, AGB_LABELS, plot_y_z


x_min = -2.8
x_max = 0.6
N_points = 100
scale = 1e4
ele = "c"

vice.yields.ccsne.settings[ele] = 0
vice.yields.sneia.settings[ele] = 0

plt.figure(figsize=(20/9, 20/9))

for i in range(4):
    model = AGB_MODELS[i]

    vice.yields.agb.settings[ele] = agb_interpolator(ele, study=model)
    kwargs = dict(fmt="o", zorder=i, factor=scale, color=arya.COLORS[i])
    
    # plots importaint points
    _y1, _m1, Zs = vice.yields.agb.grid('c', study=model)
    (line,), _x = plot_y_z(Zs, **kwargs)
    
    # plot solid within range
    MoverH_min = Z_to_MH(min(Zs))
    MoverH_max = Z_to_MH(max(Zs))
    
    kwargs["fmt"] = "-"
    Zs = MH_to_Z(np.linspace(MoverH_min, MoverH_max, N_points))
    plot_y_z(Zs, label=AGB_LABELS[model], **kwargs)

    # dashed extrapolation
    kwargs["fmt"] = "--"
    Zs = MH_to_Z(np.linspace(x_min, MoverH_min, N_points))    
    plot_y_z(Zs, **kwargs)
    Zs = MH_to_Z(np.linspace(MoverH_max, x_max, N_points))
    plot_y_z(Zs, **kwargs)





arya.Legend(color_only=True, handlelength=0, ncols=2, columnspacing=1, loc=3, transpose=True)
plt.ylabel(r"integrated AGB C yield $\quad [\times 10^{-4}]$")
plt.savefig("figures/y_agb_vs_z.pdf")
