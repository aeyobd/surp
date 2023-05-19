import matplotlib.pyplot as plt
import vice
import numpy as np
import matplotlib as mpl

import plot_style

colors = plot_style.COLORS

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

for i in range(len(ccsne_studies)):
    study=ccsne_studies[i]
    metalicities = allowed_MoverH[study]
    rotations = allowed_rotations[study]
    m_upper = M_max[study]
    
    for j in range(len(rotations)):
        rotation = rotations[j]
        yc = [vice.yields.ccsne.fractional('c', study=study, MoverH=metalicity, 
            rotation=rotation, m_upper=m_upper)[0]
             for metalicity in metalicities]
        yo = [vice.yields.ccsne.fractional('o', study=study, MoverH=metalicity, 
            rotation=rotation, m_upper=m_upper)[0]
              for metalicity in metalicities]
        y = np.log10(np.array(yc)/yo) - np.log10(vice.solar_z("c")/vice.solar_z("o"))
        
        Z = list(map(lambda x: 10**x, metalicities))
        if rotation == 0:
            marker = ["v", "o", "*", "s"][i]
        elif rotation == 150:
            marker=">"
        elif rotation == 300:
            marker="^"
        plt.scatter(np.log10(Z), y, color=colors[i], label=f"{study}, v={rotation}", marker=marker)


# plot model ...
def y_c_cc(Z):
    return 0.005 * (Z/0.014)**0.3

m_h = np.linspace(-0.6, 0.6, 1000)
Z = 0.014*10**m_h
y = np.log10(y_c_cc(Z)/0.015) - np.log10(vice.solar_z("c")/vice.solar_z("o"))
plt.plot(m_h, y, color="k")

m_h = np.linspace(-4, -0.6, 1000)
Z = 0.014*10**m_h
y = np.log10(y_c_cc(Z)/0.015) - np.log10(vice.solar_z("c")/vice.solar_z("o"))
plt.plot(m_h, y, color="k", ls="--")


# final style things
plt.xlabel(r"$\log Z/Z_{\odot}$")
plt.ylabel(r"[C/O]$^\text{CC}$")

plot_style.save()
