import matplotlib.pyplot as plt

import sys
import pandas as pd
from mcmc_setup import results


result = results["fruity"]

fig = plt.figure(figsize=(3.3, 3.3))

result.plot_corner( 
    fig = fig,
    labels={
        "alpha": r"$\alpha$",
        "y0_cc": r"$\zeta_{0}$",
        "zeta_cc": r"$\zeta_{1}$",
        "A_cc": r"$\zeta_{2}$",},
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
