import matplotlib.pyplot as plt
import numpy as np
import vice
from . import apogee_analysis as aah


def plot_c_table(study = "cristallo11", ax=None, fig=None, **kwargs):
    if ax is None:
        fig, ax = plt.subplots()
    Z_max = 0.02
    Z_min = 0.0001

    y1, m1, z1 = vice.yields.agb.grid('c', study=study)
    cmap = plt.get_cmap('jet')
    N = len(z1)

    for i in range(N):
        y = np.array(y1)[:,i]
        z = z1[i]
        c = (np.log(z) - np.log(Z_min))/np.log(Z_max/Z_min)
        f = ax.plot(m1, y, label=f"Z = {z}", c=cmap(c), **kwargs)

    #ax.set_xlabel("stellar mass")
    #ax.set_ylabel("$y_C^{agb}$")
    ax.set_title(study)
    # fig.legend()
    return f

# def func?
#     Z_vals = [0.0001,0.0003,0.001,0.002,0.003,0.006, 0.008, 0.01, 0.014, 0.02]
#     cmap = plt.get_cmap("jet")
#     fig, ax = plt.subplots()
#     for i in range(len(Z_vals)):
#         Z = Z_vals[i]
#         x = np.linspace(1, 6, 1000)
#         y = f(x, Z)
#         plt.plot(x, y, label=Z, c=cmap(i/len(Z_vals)))
#     plt.axhline(0)
#     plot_c_table("cristallo11", marker="o", ms=2, lw=0, ax=ax, fig=fig)


def plot_agb_z(f, ax=None):
    if ax is None:
        ax = plt.gca()

    for model in ["cristallo11", "karakas10","ventura13", "karakas16"]:
        vice.yields.agb.settings["c"] = model
        Zs = 0.014*10**np.linspace(-2, 1, 100)
        if type(model) == str:
            y1, m1, z1 = vice.yields.agb.grid('c', study=model)
            Zs = np.array(z1)
        mass_yields = []
        for Z in Zs:
            m_c, times = vice.single_stellar_population("c", Z=Z)
            mass_yields.append(m_c[-1])
        
        ax.plot(np.log10(Zs/0.014), np.array(mass_yields)/1e6 - 0.002, label=model, marker="o")

    Zs = 0.014 * 10 **np.linspace(-2, 1, 100)
    ax.plot(np.log10(Zs/0.014), f(Zs), label="analytic")
    ax.set(xlabel = r"$\log Z/Z_\odot$", ylabel = "$y_C^{agb}$", ylim = (-2e-3, 3e-3))
    ax.axhline(0, c="black", linestyle="--")
    ax.scatter(0, vice.solar_z("c"), marker="*", color="green", label="sun")


# ------------------ CCSNe -------------------
allowed_MoverH = {
    "LC18": [-3, -2, -1, 0],
    "S16/N20": [0],
    "CL13": [0],
    "NKT13": [-np.inf, -1.15, -0.54, -0.24, 0.15, 0.55],
    "CL04": [-np.inf, -4, -2, -1, -0.37, 0.15],
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

def plot_ycc(ele="c", ax=None):
    if ax is None:
        ax = plt.gca()
    for i in range(N):
        study=ccsne_studies[i]
        metalicities = allowed_MoverH[study]
        rotations = allowed_rotations[study]

        for j in range(len(rotations)):
            rotation = rotations[j]
            y = [vice.yields.ccsne.fractional(ele, study=study, MoverH=metalicity, rotation=rotation)[0]
                 for metalicity in metalicities]

            Z = list(map(lambda x: 10**x, metalicities))
            if rotation == 0:
                marker = "o"
            elif rotation == 150:
                marker="+"
            elif rotation == 300:
                marker="^"
            ax.scatter(np.log10(Z), y, color=cmap(i/N), label=f"{study}, v={rotation}", marker=marker)

    ax.legend()
    ax.axhline(0.002)
    #plt.xscale("log")
    ax.set_ylim([0, 0.008])

    ax.set_xlabel("[M/H]")
    ax.set_ylabel(r"$y_C^{cc}$")

def plot_ycyo(ax=None, scaled=True):
    if ax is None:
        ax = plt.gca()

    for i in range(len(ccsne_studies)):
        study=ccsne_studies[i]
        metalicities = allowed_MoverH[study]
        rotations = allowed_rotations[study]

        for j in range(len(rotations)):
            rotation = rotations[j]
            yc = [vice.yields.ccsne.fractional('c', study=study, MoverH=metalicity, rotation=rotation)[0]
                 for metalicity in metalicities]
            yo = [vice.yields.ccsne.fractional('o', study=study, MoverH=metalicity, rotation=rotation)[0]
                  for metalicity in metalicities]
            y = np.log10(np.array(yc)/yo) 
            if scaled:
                y -= np.log10(vice.solar_z("c")/vice.solar_z("o"))

            Z = list(map(lambda x: 10**x, metalicities))
            if rotation == 0:
                marker = "o"
            elif rotation == 150:
                marker="+"
            elif rotation == 300:
                marker="^"
            ax.scatter(np.log10(Z), y, color=cmap(i/N), label=f"{study}, v={rotation}", marker=marker)

    # ax.axhline(0)
    # ax.axhline(-0.49, ls="--")


    #plt.ylim([0, 0.008])
    ax.set_xlabel("[M/H]")
    ax.set_ylabel(r"$\log y_C^{cc}/y_O^{cc}$, scaled to solar [C/O]")
