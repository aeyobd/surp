import matplotlib.pyplot as plt
import vice
import numpy as np
import matplotlib as mpl

import sys
sys.path.append("../..")

from surp.src.analysis.plotting_utils import fig_saver


sf = fig_saver("figures")

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
plt.ylim(0, 0.0055)
#plt.legend(bbox_to_anchor=(1,1), loc="upper left")
def y_c_cc(Z):
    return 0.004 *(0.5 + (Z/0.014)**0.3)/1.5

m_h = np.linspace(-0.6, 0.5, 1000)
Z = 0.014*10**m_h
plt.plot(m_h, y_c_cc(Z), color="k")

# plot AGB line

vice.yields.agb.settings["c"] = "cristallo11"
vice.yields.ccsne.settings["c"] = 0
Zs = 0.014*10**np.linspace(-2, 1, 100)

# plots importaint points
y1, m1, z1 = vice.yields.agb.grid('c', study="cristallo11")
Zs = np.array(z1)
mass_yields = []
for Z in Zs:
    m_c, times = vice.single_stellar_population("c", Z=Z)
    mass_yields.append(m_c[-1])
    
y_c_agb = np.array(mass_yields)/1e6 
y_o_cc = 0.015
# plt.scatter(np.log10(Zs/0.014), y_c_agb)
MoverH_min = np.log10(min(Zs)/0.014)
MoverH_max = np.log10(max(Zs)/0.014)

Zs = 0.014*10**np.linspace(MoverH_min, MoverH_max, 100)
mass_yields = []
for Z in Zs:
    m_c, times = vice.single_stellar_population("c", Z=Z)
    mass_yields.append(m_c[-1])
line, = plt.plot(np.log10(Zs/0.014), (np.array(mass_yields)/1e6 ), label="C11 (AGB)")

color = line.get_color()

Zs = 0.014*10**np.linspace(-2.1, MoverH_min, 100)
mass_yields = []
for Z in Zs:
    m_c, times = vice.single_stellar_population("c", Z=Z)
    mass_yields.append(m_c[-1])
#plt.plot(np.log10(Zs/0.014), (np.array(mass_yields)/1e6 ), linestyle="--", color=color)

Zs = 0.014*10**np.linspace(MoverH_max, 0.6, 100)
mass_yields = []
for Z in Zs:
    m_c, times = vice.single_stellar_population("c", Z=Z)
    mass_yields.append(m_c[-1])
# plt.plot(np.log10(Zs/0.014), (np.array(mass_yields)/1e6 ), linestyle="--", color=color)

m_h = np.linspace(-4, -0.6, 1000)
Z = 0.014*10**m_h
plt.plot(m_h, y_c_cc(Z), color="k", ls="--")

plt.legend(bbox_to_anchor=(1,1), loc="upper left")

#x = np.linspace(-4, 1)
#y = y_cc(0.014*10**x)
#plt.plot(x, y)
plt.xlabel(r"$\log Z/Z_\odot$")
plt.ylabel(r"$Y_{\rm C}^{\rm CC}$")
sf("y_c_cc")
