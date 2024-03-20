import matplotlib.pyplot as plt
import argparse

import sys
import os
import numpy as np

from surp import ViceModel, subgiants
from surp import plots as sp

import seaborn as sns
import arya


def main():
    arya.style.init()
    filename, output = parse_args()
    plot_model(filename, output)


def plot_model(filename, plots_dir="figures"):
    if not os.path.exists(plots_dir):
        raise FileNotFoundError("directory does not exist ", filename, "failed to make directory")
        return

    print("loading model")
    model = ViceModel.from_saved(filename)
    stars = sp.add_scatter(model.stars)

    pwd = os.getcwd()
    print("cd ", plots_dir)
    os.chdir(plots_dir)

    print("plotting")

    plot_mdf(model.history)
    plt.savefig("mdf.pdf")
    plt.close()

    plot_mdf(model.history, x="MG_FE")
    plt.savefig("mdf_o_fe.pdf")
    plt.close()

    plot_tracks(model.history)
    plt.savefig("cooh_gas.pdf")
    plt.close()

    plot_tracks(model.history, x="MG_FE")
    plt.savefig("coofe_gas.pdf")
    plt.close()

    plot_cooh(stars)
    plt.savefig("cooh.pdf")
    plt.close()

    plot_coofe(stars)
    plt.savefig("coofe.pdf")
    plt.close()


    plot_ofefeh(stars)
    plt.savefig("ofefeh.pdf")
    plt.close()

    os.chdir(pwd)



def parse_args():
    parser = argparse.ArgumentParser(description="Makes a few plots of a vice model")
    parser.add_argument("filename", help="path to surp .json model", type=str)
    parser.add_argument("-o", "--output", default="./", type=str)

    args = parser.parse_args()

    return args.filename, args.output




def to_label(x):
    ele1, ele2 = x.split("_")
    ele1 = ele1.title()
    ele2 = ele2.title()
    return "[%s/%s]" % (ele1, ele2)

def plot_mdf(history, x="FE_H"):
    kwargs = dict(
            histtype="step",
            density=True,
            range=(-0.3, 0.7),
            bins=100
            )
    plt.hist(history[x], label="model", **kwargs)
    plt.hist(subgiants[x], label="data", **kwargs)
    plt.xlabel(to_label(x))
    plt.ylabel("density")
    arya.Legend()



def plot_tracks(history, x="MG_H", y="C_MG", Rs=[4,6,8,10,12]):
    for R in Rs:
        df = history[np.isclose(history.R, R-0.05)]
        plt.plot(df[x], df[y], color="k")

    sns.scatterplot(history, x=x, y=y, hue="time", s=0.3, alpha=1,
            legend=False, edgecolor="none", palette="arya_r")
    plt.xlim(-1.2, 0.6)
    plt.ylim(-0.6, 0.2)
    plt.xlabel(to_label(x))
    plt.ylabel(to_label(y))
    arya.Colorbar(clim=(0, 13.2), label="t (Gyr)", cmap="arya_r")



def plot_cooh(df):
    df = sp.filter_high_alpha(df)
    sns.scatterplot(df, x="MG_H", y="C_MG", hue="r_origin", s=0.3, alpha=1,
            legend=False, edgecolor="none", palette="arya_r")

    df = sp.filter_high_alpha(subgiants)
    sns.kdeplot(df, x="MG_H", y="C_MG", lw=1, color="k", zorder=3)

    plt.xlim(-0.8, 0.8)
    plt.ylim(-0.4, 0.2)

    plt.xlabel("[Mg/H]")
    plt.ylabel("[C/Mg]")


def plot_coofe(stars):
    df = sp.filter_metallicity(subgiants)
    sns.kdeplot(df, x="MG_FE", y="C_MG", lw=1, color="k", zorder=3)

    df = sp.filter_metallicity(stars)
    plt.scatter(df["MG_FE"], df["C_MG"], c=df["r_origin"], s=0.3, zorder=2)

    plt.xlim(-0.1, 0.5)
    plt.ylim(-0.4, 0.2)

    plt.xlabel("[Mg/Fe]")
    plt.ylabel("[C/Mg]")


def plot_ofefeh(df):
    sns.scatterplot(df, x="FE_H", y="MG_FE", hue="r_origin", s=0.3, alpha=1,
            legend=False, edgecolor="none", palette="arya_r")

    sns.kdeplot(subgiants, x="FE_H", y="MG_FE", zorder=3, exclude_high_alpha=False)

    plt.xlim(-1, 0.5)
    plt.ylim(-0.1, 0.5)
    plt.xlabel("[Fe/H]")
    plt.ylabel("[Mg/Fe]")



if __name__ == "__main__":
    main()
