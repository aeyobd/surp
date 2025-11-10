import matplotlib.pyplot as plt

import sys
import pandas as pd
from mcmc_setup import results


result = results["fruity"]

fig = plt.figure(figsize=(3.3, 3.3))

result.samples.y0_cc *= 10
result.samples.zeta_cc *= 10

result.plot_corner( 
    fig = fig,
    labels={
        "alpha": r"$\beta_{\rm C}^{\rm AGB}$",
        "y0_cc": r"$y_{\rm low} / 10^{-4}$",
        "zeta_cc": r"$\zeta_{\rm C}^{\rm CC} / 10^{-4}$",
        },
    labelpad=0.15,
    title_kwargs = {
        "fontsize": 6,
    }
   )

# correct ticks
for ax in fig.get_axes():
    ax.tick_params(axis='x', labelrotation=90)
    ax.tick_params(axis='y', labelrotation=0)

plt.savefig("figures/mcmc_corner.pdf")
plt.savefig("figures/mcmc_corner.png")
