import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass

import vice

import sys
sys.path.append("../")

from src.analysis.vice_model import vice_model
import src.analysis.apogee_analysis as aah
import src.analysis.plotting_utils as pluto

sf = pluto.fig_saver("./figures")

@dataclass
class model_id():
    agb: str = None
    eta: str = None
    f_agb: str = None
    beta: str = None
    name: str = None
    version: str = ""


def find_model(id):
    """
    Finds the pickled model with either the given name or the parameters 
    and returns the vice_model object
    """
    if id.name is None:
        name = id.agb + "_f" + id.f_agb + "_Z" + id.beta + "_eta" + id.eta + id.version
    else:
        name = id.name
    file_name = "../output/" + name + ".json"
    return vice_model(file_name)


fiducial = find_model(model_id(agb="cristallo11", f_agb="0.2", eta="1.0",
    beta="0.4", version="_v0.1.3"))

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
    xticks=np.arange(-1,0.7,1)
)

fiducial.plot_R_slices("[o/fe]", "[c/o]", ax=axs[1], legend=False)
axs[1].set(
    ylabel="",
    xlabel=r"[$\alpha$/Fe]"
)

sf("evo_tracks")
