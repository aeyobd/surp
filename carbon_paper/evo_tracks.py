import matplotlib.pyplot as plt
import numpy as np

import vice

import sys
sys.path.append("../")

import src.analysis.apogee_analysis as aah
import src.analysis.plotting_utils as pluto

import plot_style
import load_model


fiducial = load_model.fiducial()

fig = plt.figure(figsize=(6.3, 3.15))
gs = fig.add_gridspec(1, 2, wspace=0)
axs = gs.subplots(sharey=True)

plt.sca(axs[0])
fiducial.plot_R_slices("[o/h]", "[c/o]", ax=axs[0])

axs[0].set(
    xlim=(-1, 0.6),
    ylim=(-0.7, 0.1),
    xlabel=r"[$\alpha$/H]",
    ylabel=r"[C/$\alpha$]",
)

fiducial.plot_R_slices("[o/fe]", "[c/o]", ax=axs[1], legend=False)
axs[1].set(
    ylabel="",
    xlabel=r"[$\alpha$/Fe]"
)

plot_style.save()
