import matplotlib.pyplot as plt
import vice
import numpy as np
import matplotlib as mpl
import sys

sys.path.append("../..")
from plotting_utils import fig_saver

sys.path.append("/home/daniel")
from python_packages.plotting import rc_params

sf = fig_saver()


cmap = mpl.cm.plasma
Z_max = 0.02
Z_min = 0.0001
AGB_MODELS = ["cristallo11", "karakas10", "ventura13", "karakas16"]
AGB_LABELS = ["C11+C15", "K10", "V13", "KL16+K18"]

def plot_c_table(study = "cristallo11", ax=None, fig=None, **kwargs):
    if ax is None:
        fig, ax = plt.subplots()

    y1, m1, z1 = vice.yields.agb.grid('c', study=study)
    N = len(z1)

    for i in range(N):
        y = np.array(y1)[:,i]
        z = z1[i]
        c = (np.log(z) - np.log(Z_min))/np.log(Z_max/Z_min)
        f = ax.plot(m1, y, label=f"Z = {z}", c=cmap(c), **kwargs)

    ax.set_title(study)
    return f


fig, axs = plt.subplots(2, 2, figsize=(12, 8), sharex=True, sharey=True)

for i in range(4):
    study = AGB_MODELS[i]
    label = AGB_LABELS[i]
    ax = axs[i//2][i%2]
    f = plot_c_table(study, ax=ax, fig=fig)
    ax.set_title(label)
    #plt.legend()



norm = mpl.colors.Normalize(vmin=np.log10(Z_min/0.014), vmax=np.log10(Z_max/0.014))
mappable = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
fig.colorbar(mappable, ax=axs.ravel().tolist(), label="[M/H]")

plt.setp(axs[-1, :], xlabel=r'$M/M_\odot$')
plt.setp(axs[:, 0], ylabel=r'$M_\text{C,net}/M$')

sf("figure1")
