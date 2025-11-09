import matplotlib.pyplot as plt
import arya
arya.style.set_size((10/3, 10/3))

import sys
sys.path.append("..")
from mw_model_plots import compare_cooh


names = ["fiducial/run"]
labels = ["fiducial model"]

compare_cooh(names, labels, y="C_N", ylim=(-0.3, 0.3), legend=False, use_true=False)

plt.scatter([], [], color="black", label="APOGEE median") 
plt.scatter([], [], color="black", alpha=0.3, marker="_", label="APOGEE 16th-84th") 
plt.legend()

plt.savefig("figures/nitrogen.pdf")
