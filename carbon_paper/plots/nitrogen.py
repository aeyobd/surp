import matplotlib.pyplot as plt
import arya
arya.style.set_size((10/3, 10/3))

import sys
sys.path.append("..")
from mw_model_plots import compare_cooh


names = ["fiducial/run"]
labels = ["fiducial"]

compare_cooh(names, labels, y="C_N", ylim=(-0.3, 0.3), legend=False, use_true=False)
plt.savefig("figures/nitrogen.pdf")
