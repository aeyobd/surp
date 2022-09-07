import matplotlib.pyplot as plt
import vice
import sys
import numpy as np

sys.path.append("../../")
from plotting_utils import fig_saver
sf = fig_saver()

sys.path.append("/home/daniel")
from python_packages.plotting import rc_params

AGB_MODELS = ["cristallo11", "karakas10", "ventura13", "karakas16"]
AGB_LABELS = ["C11+C15", "K10", "V13", "KL16+K18"]



for i in range(len(AGB_MODELS)):
    model = AGB_MODELS[i]

    vice.yields.agb.settings["c"] = model
    vice.yields.ccsne.settings["c"] = 0
    Zs = 0.014*10**np.linspace(-2, 1, 100)
    
    # plots importaint points
    if type(model) == str:
        y1, m1, z1 = vice.yields.agb.grid('c', study=model)
        Zs = np.array(z1)
    mass_yields = []
    for Z in Zs:
        m_c, times = vice.single_stellar_population("c", Z=Z)
        mass_yields.append(m_c[-1])
        
    y_c_agb = np.array(mass_yields)/1e6 
    y_o_cc = 0.015
    plt.scatter(np.log10(Zs/0.014), y_c_agb/y_o_cc)
    MoverH_min = np.log10(min(Zs)/0.014)
    MoverH_max = np.log10(max(Zs)/0.014)
    
    Zs = 0.014*10**np.linspace(MoverH_min, MoverH_max, 100)
    mass_yields = []
    for Z in Zs:
        m_c, times = vice.single_stellar_population("c", Z=Z)
        mass_yields.append(m_c[-1])
    line, = plt.plot(np.log10(Zs/0.014), (np.array(mass_yields)/1e6 )/y_o_cc, label=AGB_LABELS[i])

    color = line.get_color()

    Zs = 0.014*10**np.linspace(-2.1, MoverH_min, 100)
    mass_yields = []
    for Z in Zs:
        m_c, times = vice.single_stellar_population("c", Z=Z)
        mass_yields.append(m_c[-1])
    plt.plot(np.log10(Zs/0.014), (np.array(mass_yields)/1e6 )/y_o_cc, linestyle="--", color=color)

    Zs = 0.014*10**np.linspace(MoverH_max, 0.6, 100)
    mass_yields = []
    for Z in Zs:
        m_c, times = vice.single_stellar_population("c", Z=Z)
        mass_yields.append(m_c[-1])
    plt.plot(np.log10(Zs/0.014), (np.array(mass_yields)/1e6 )/y_o_cc, linestyle="--", color=color)

plt.xlabel(r"[M/H]")
plt.ylabel(r"$y_\text{C}^\text{AGB}$")

plt.legend()
sf("figure1c")
