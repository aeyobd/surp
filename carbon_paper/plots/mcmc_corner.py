import matplotlib.pyplot as plt

import sys
sys.path.append("..")
from mc_plot_utils import MCMCResult
import pandas as pd


def load_model(filename, props, test=False, burn=0):
    y0 = props["y0"],
    y_a = props["y_a"]
    zeta_a = props["zeta_a"]
    
    if test:
        result = MCMCResult.from_test_file(filename, burn=burn)
    else:
        result = MCMCResult.from_file(filename, y0=y0, burn=burn, y_a=y_a, zeta_a=zeta_a)
    return result


df = pd.read_csv("../yield_fits.tsv", sep=r"\s+", comment="#")
yagb_props = {}

for _, row in df.iterrows():
    yagb_props[row.model] = {
        "y0": row.y0 * 1e-4,
        "y_a": row.zeta0 * 1e-4,
        "zeta_a": row.zeta1 * 1e-4,
    }


fig = plt.figure(figsize=(3.3, 3.3))

result = load_model("fiducial", yagb_props["fruity"])

result.plot_corner( 
    fig = fig,
    labels={
        "alpha": r"$\alpha$",
        "y0_cc": r"$\zeta^{(0)}$",
        "zeta_cc": r"$\zeta^{(1)}$",
        "A_cc": r"$\zeta^{(2)}$",},
    labelpad=0.1,
    title_kwargs = {
        "fontsize": 6,
    }
   )

plt.savefig("figures/mcmc_corner.pdf")
plt.savefig("figures/mcmc_corner.png")
