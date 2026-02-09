import arya
import matplotlib.pyplot as plt
import matplotlib as mpl

import sys
sys.path.append("..")
from yield_plot_utils import AGB_MODELS, AGB_LABELS, plot_yield_table, hmap


SCALE_FACTOR=1e2
fig, ax = plt.subplots(1, 1, figsize=(20/9, 20/9), sharex=True, sharey=True, gridspec_kw={"hspace":0, "wspace": 0, "left": 0.1})

for i in range(1):
    study = AGB_MODELS[i]
    label = AGB_LABELS[study]
    f = plot_yield_table(study, ax=ax, 
                         fig=fig, fmt="o", factor=SCALE_FACTOR)
    
    # plot label
    ax.text(0.95, 0.9, label, horizontalalignment='right',
            verticalalignment='top', transform=ax.transAxes)
    


arya.Colorbar(huemap=hmap, ax=ax,
              label=r"Metallicity ($\log Z/Z_\odot$)")

plt.xlabel(r'initial mass / ${\rm M}_\odot$')
plt.ylabel(r"stellar C yield $\quad[\times 10^{-2}]$")

plt.gca().xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))

plt.savefig("figures/agb_cristallo.pdf")
