import matplotlib.pyplot as plt
import vice
import sys
import numpy as np

sys.path.append("../..")
from surp.analysis_scripts.plotting_utils import fig_saver
import surp.analysis_scripts.rc_params

sf = fig_saver()


AGB_MODELS = ["cristallo11", "karakas10", "ventura13", "karakas16"]
AGB_LABELS = ["C11+C15", "K10", "V13", "KL16+K18"]
vice.yields.ccsne.settings["c"] = 0
vice.yields.sneia.settings["c"] = 0
vice.yields.ccsne.settings["fe"] = 0

for i in range(4):
    model = AGB_MODELS[i]
    vice.yields.agb.settings["c"] = model
    m_c, times = vice.single_stellar_population("c", Z=0.014 * 10**0)
    m_c = [c for c in m_c]
    plt.plot(times, np.array(m_c)/m_c[-1])

m_fe, times = vice.single_stellar_population("fe", Z=0.014)
m_fe = [fe for fe in m_fe]
plt.plot(times, np.array(m_fe)/m_fe[-1], label="SN Ia Fe",
         linestyle="--", color="k")


plt.xlabel("t/Gyr")
plt.ylabel(r"$M_X/M_{X,\text{final}}$")
plt.xscale("log")
plt.legend()
plt.ylim(-0.3, 1.1)
plt.xlim(0.03, 13.2)
sf("y_agb_vs_t")

