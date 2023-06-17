import matplotlib.pyplot as plt
import matplotlib.patheffects
import matplotlib as mpl

import sys
import os
import numpy as np


from surp.analysis.vice_model import vice_model
from surp.analysis import apogee_analysis as aah
import seaborn as sns
import arya


def main():
    filename = get_args()
    directory = make_dir(filename)
    print("created dir ", directory)

    print("loading model")
    model = vice_model(filename)

    os.chdir(directory)
    print("plotting")
    plot_mdf(model)
    plt.savefig("mdf.pdf")

    plot_cooh_tracks(model)
    plt.savefig("cooh_gas.pdf")

    plot_coofe_tracks(model)
    plt.savefig("coofe_gas.pdf")

    plot_cooh(model)
    plt.savefig("cooh.pdf")

    plot_coofe(model)
    plt.savefig("coofe.pdf")
    os.chdir("..")


def get_args():
    if len(sys.argv) != 2:
        raise RuntimeError("requires 1 arg, name of model")
    filename = sys.argv[1]
    
    if not os.path.exists(filename):
        raise RuntimeError("file not found ", filename)
    return filename


def make_dir(filename):
    dirname, _ = os.path.splitext(os.path.basename(filename))
    if os.path.exists(dirname):
        raise RuntimeError("directory already exists")
    os.mkdir(dirname)
    return dirname


def plot_mdf(model):
    df = model.history
    kwargs = dict(
            histtype="step",
            density=True,
            range=(-0.3, 0.7),
            bins=100
            )
    plt.hist(df["[o/fe]"], label="model", **kwargs)
    plt.hist(aah.subgiants["MG_FE"], label="data", **kwargs)
    plt.xlabel("[Mg/Fe]")
    plt.ylabel("density")
    arya.Legend()


def plot_cooh_tracks(model):
    h = model.history

    for R in [4, 6, 8, 10, 12]:
        df = h[np.isclose(h.R, R-0.05)]
        plt.plot(df["[o/h]"], df["[c/o]"], color="k")

    sns.scatterplot(h, x="[o/h]", y="[c/o]", hue="time", s=0.3, alpha=1,
            legend=False, edgecolor="none")
    plt.xlim(-0.8, 0.8)
    plt.ylim(-0.3, 0.13)
    plt.xlabel("[Mg/H]")
    plt.ylabel("[C/Mg]")
    arya.Colorbar(clim=(0, 13.2), label="t (Gyr)", cmap="arya_r")

def plot_coofe_tracks(model):
    h = model.history

    for R in [4, 6, 8, 10, 12]:
        df = h[np.isclose(h.R, R-0.05)]
        plt.plot(df["[o/fe]"], df["[c/o]"], color="k")

    sns.scatterplot(h, x="[o/fe]", y="[c/o]", hue="time", s=0.3, alpha=1,
            legend=False, edgecolor="none")
    plt.xlim(-0.05, 0.4)
    plt.ylim(-0.2, 0.1)
    plt.xlabel("[Mg/Fe]")
    plt.ylabel("[C/Mg]")
    arya.Colorbar(clim=(0, 13.2), label="t (Gyr)", cmap="arya_r")




def plot_cooh(model):
    s = model.stars
    dx = 0.03
    dy = 0.03
    N = len(s)

    aah.plot_contour("[mg/h]", "[c/mg]", zorder=3)
    plt.scatter(s["[mg/h]"] + np.random.normal(0, dx, N),
            s["[c/mg]"] + np.random.normal(0, dx, N),
            c=s["r_origin"], s=0.3, zorder=2)

    plt.xlim(-0.8, 0.8)
    plt.ylim(-0.3, 0.13)

    plt.xlabel("[Mg/H]")
    plt.ylabel("[C/Mg]")


def plot_coofe(model):
    oo = -0.1
    do = 0.05

    filt = model.stars > oo - do
    filt &= model.stars < oo + do
    s = model.stars[filt]


    filt = aah.subgiants > oo - do
    filt &= aah.subgiants < oo + do
    df = aah.subgiants[filt]

    dx = 0.03
    dy = 0.03
    N = len(s)

    sns.contourplot(df, x="[mg/fe]", y="[c/mg]", color="k")

    plt.scatter(s["[mg/fe]"] + np.random.normal(0, dx, N),
            s["[c/mg]"] + np.random.normal(0, dx, N),
            c=s["r_origin"], s=0.3, zorder=2)

    plt.xlim(-0.8, 0.8)
    plt.ylim(-0.3, 0.13)

    plt.xlabel("[Mg/Fe]")
    plt.ylabel("[C/Mg]")







if __name__ == "__main__":
    main()
