import matplotlib.pyplot as plt
import vice
import numpy as np
import matplotlib as mpl
import sys
sys.path.append("../../")
from plotting_utils import fig_saver

sys.path.append("/home/daniel")
from python_packages.plotting import rc_params

sf = fig_saver()

colors = ['#0072B2', '#009E73', '#D55E00', '#CC79A7', '#F0E442', '#56B4E9']

allowed_MoverH = {
    "LC18": [-3, -2, -1, 0],
    "S16/N20": [0],
    #"CL13": [0],
    "NKT13": [-np.inf, -1.15, -0.54, -0.24, 0.15, 0.55],
    #"CL04": [-np.inf, -4, -2, -1, -0.37, 0.15],
    "WW95": [-np.inf, -4, -2, -1, 0]
    }
allowed_rotations = {
    "LC18": [0, 150, 300],
    "S16/N20": [0],
    "CL13": [0, 300],
    "NKT13": [0],
    "CL04": [0],
    "WW95": [0]
}

ccsne_studies = ["LC18", "S16/N20", "WW95","NKT13"]
cmap = plt.get_cmap("jet")
N = len(ccsne_studies)


for i in range(N):
    study=ccsne_studies[i]
    metalicities = allowed_MoverH[study]
    rotations = allowed_rotations[study]
    
    for j in range(len(rotations)):
        rotation = rotations[j]
        y = [vice.yields.ccsne.fractional('c', study=study, MoverH=metalicity, rotation=rotation)[0]
             for metalicity in metalicities]
        
        Z = list(map(lambda x: 10**x, metalicities))
        if rotation == 0:
            marker = ["v", "o", "*", "s"][i]
        elif rotation == 150:
            marker=">"
        elif rotation == 300:
            marker="^"
        plt.scatter(np.log10(Z), y, color=colors[i], label=f"{study}, v={rotation}", marker=marker)

#plt.axhline(0.002, ls="--", color="k", zorder=-1, label="fiducial")
#plt.xscale("log")
plt.ylim([0, 0.008])
#plt.legend(bbox_to_anchor=(1,1), loc="upper left")
m_h = np.linspace(-4, 1, 1000)
def y_c_cc(Z):
    return 0.02 * Z**0.25
Z = 0.014*10**m_h
plt.plot(m_h, y_c_cc(Z), color=colors[5], label="adjusted")

plt.axhline(0.005, linestyle="--", color="k", label="fiducial")

plt.legend(bbox_to_anchor=(1,1), loc="upper left")

#x = np.linspace(-4, 1)
#y = y_cc(0.014*10**x)
#plt.plot(x, y)
plt.xlabel("[M/H]")
plt.ylabel(r"$y_C^{CC}$")
sf("figure2")