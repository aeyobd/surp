import matplotlib.pyplot as plt
import vice
import numpy as np
import matplotlib as mpl

import plot_style


colors = plot_style.COLORS

# some studies have -inf values, which are ignored
allowed_MoverH = {
    "LC18": [-3, -2, -1, 0],
    "S16/N20": [0],
    #"CL13": [0],
    "NKT13": [-1.15, -0.54, -0.24, 0.15, 0.55],
    #"CL04": [-np.inf, -4, -2, -1, -0.37, 0.15],
    "WW95": [-4, -2, -1, 0]
    }

allowed_rotations = {
    "LC18": [0, 150, 300],
    "S16/N20": [0],
    "CL13": [0, 300],
    "NKT13": [0],
    "CL04": [0],
    "WW95": [0]
}

M_max = {
    "LC18": 120,
    "S16/N20": 120,
    "NKT13": 40,
    "WW95": 40,
    "CL04": 35,
    "CL13": 120,
}

ccsne_studies = ["LC18", "S16/N20", "WW95","NKT13"]

N = len(ccsne_studies)


for i in range(N):
    study=ccsne_studies[i]
    metalicities = allowed_MoverH[study]
    rotations = allowed_rotations[study]
    m_upper = M_max[study]
    
    for j in range(len(rotations)):
        rotation = rotations[j]
        y = [vice.yields.ccsne.fractional('c', study=study, MoverH=metalicity, 
            rotation=rotation, m_upper=m_upper)[0]
             for metalicity in metalicities]
        
        Z = list(map(lambda x: 10**x, metalicities))
        if rotation == 0:
            marker = ["v", "o", "*", "s"][i]
        elif rotation == 150:
            marker=">"
        elif rotation == 300:
            marker="^"
        plt.scatter(np.log10(Z), y, color=colors[i], label=f"{study}, v={rotation}", marker=marker)


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

m_h = np.linspace(-4, -0.6, 1000)
Z = 0.014*10**m_h
plt.plot(m_h, y_c_cc(Z), color="k", ls="--")

plt.legend(bbox_to_anchor=(1,1), loc="upper left")

#x = np.linspace(-4, 1)
#y = y_cc(0.014*10**x)
#plt.plot(x, y)
plt.xlabel(r"$\log Z/Z_\odot$")
plt.ylabel(r"$Y_{\rm C}^{\rm CC}$")

plot_style.save()
