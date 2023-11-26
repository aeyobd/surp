import matplotlib.pyplot as plt

import sys
import os
import numpy as np


from surp import ViceModel, subgiants
from surp.analysis import apogee_analysis as aah

import seaborn as sns
import arya


def main():
    arya.style.init()
    filenames = get_args()
    for f in filenames:
        plot_model(f)

def plot_model(filename):
    directory = make_dir(filename)
    if not directory:
        print("skipping ", filename)
        return

    print("loading model")
    model = ViceModel(filename)

    pwd = os.getcwd()
    print("cd ", directory)
    os.chdir(directory)

    print("plotting")

    plot_mdf(model)
    plt.savefig("mdf_fe.pdf")
    plt.close()

    plot_mdf2(model)
    plt.savefig("mdf.pdf")
    plt.close()

    plot_cooh_tracks(model)
    plt.savefig("cooh_gas.pdf")
    plt.close()

    plot_coofe_tracks(model)
    plt.savefig("coofe_gas.pdf")
    plt.close()

    plot_cooh(model)
    plt.savefig("cooh.pdf")
    plt.close()

    plot_coofe(model)
    plt.savefig("coofe.pdf")
    plt.close()


    plot_ofefeh(model)
    plt.savefig("ofefeh.pdf")
    plt.close()

    print("cd ", pwd)
    os.chdir(pwd)


def get_args():
    if len(sys.argv) < 2:
        raise RuntimeError("requires at least 1 arg, name of model")
    filenames = sys.argv[1:]
    
    for filename in filenames:
        if not os.path.exists(filename):
            raise RuntimeError("file not found ", filename)
    return filenames


def make_dir(filename):
    dirname, _ = os.path.splitext(os.path.basename(filename))
    dirname = os.path.join("figures/", dirname)
    if os.path.exists(dirname):
        print("directory already exits: ", dirname)
        overwrite = input("overwrite? (y/N)")
        if overwrite != "y":
            return False
    else:
        print("creating ", dirname)
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
    plt.hist(subgiants["MG_FE"], label="data", **kwargs)
    plt.xlabel("[Mg/Fe]")
    plt.ylabel("density")
    arya.Legend()

def plot_mdf2(model):
    df = model.history
    kwargs = dict(
            histtype="step",
            density=True,
            range=(-0.3, 0.7),
            bins=100
            )
    plt.hist(df["[o/h]"], label="model", **kwargs)
    plt.hist(subgiants["MG_H"], label="data", **kwargs)
    plt.xlabel("[Mg/H]")
    plt.ylabel("density")
    arya.Legend()

def plot_cooh_tracks(model):
    h = model.history

    for R in [4, 6, 8, 10, 12]:
        df = h[np.isclose(h.R, R-0.05)]
        plt.plot(df["[o/h]"], df["[c/o]"], color="k")

    sns.scatterplot(h, x="[o/h]", y="[c/o]", hue="time", s=0.3, alpha=1,
            legend=False, edgecolor="none", palette="arya_r")
    plt.xlim(-1.2, 0.6)
    plt.ylim(-0.6, 0.2)
    plt.xlabel("[Mg/H]")
    plt.ylabel("[C/Mg]")
    arya.Colorbar(clim=(0, 13.2), label="t (Gyr)", cmap="arya_r")

def plot_coofe_tracks(model):
    h = model.history

    for R in [4, 6, 8, 10, 12]:
        df = h[np.isclose(h.R, R-0.05)]
        plt.plot(df["[o/fe]"], df["[c/o]"], color="k")

    sns.scatterplot(h, x="[o/fe]", y="[c/o]", hue="time", s=0.3, alpha=1,
            legend=False, edgecolor="none", palette="arya_r")
    plt.xlim(-0.1, 0.5)
    plt.ylim(-0.6, 0.2)
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
    plt.ylim(-0.4, 0.2)

    plt.xlabel("[Mg/H]")
    plt.ylabel("[C/Mg]")


def plot_coofe(model):
    oo = -0.1
    do = 0.05

    filt = model.stars["[o/h]"] > oo - do
    filt &= model.stars["[o/h]"] < oo + do
    s = model.stars[filt]


    filt = subgiants["MG_H"] > oo - do
    filt &= subgiants["MG_H"] < oo + do
    df = subgiants[filt]

    dx = 0.03
    dy = 0.03
    N = len(s)

    aah.plot_coofe_contour(oo, do)

    plt.scatter(s["[mg/fe]"] + np.random.normal(0, dx, N),
            s["[c/mg]"] + np.random.normal(0, dx, N),
            c=s["r_origin"], s=0.3, zorder=2)

    plt.xlim(-0.1, 0.5)
    plt.ylim(-0.4, 0.2)

    plt.xlabel("[Mg/Fe]")
    plt.ylabel("[C/Mg]")


def plot_ofefeh(model):
    s=  model.stars
    N = len(s)
    dx = 0.025
    dy = 0.025

    x = s["[fe/h]"] + np.random.normal(0, dx, N)
    y = s["[mg/fe]"] + np.random.normal(0, dy, N)
    aah.plot_contour("[fe/h]", "[mg/fe]", zorder=3, exclude_high_alpha=False)
    plt.scatter(x, y, c=s["r_origin"], s=0.03, zorder=2)

    plt.xlim(-1, 0.5)
    plt.ylim(-0.1, 0.5)
    plt.xlabel("[Fe/H]")
    plt.ylabel("[Mg/Fe]")



if __name__ == "__main__":
    main()
