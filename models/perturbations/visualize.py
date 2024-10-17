import argparse

import warnings

import sys
import os
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

import vice

import arya

from surp import ViceModel, subgiants
from surp import plots as sp
import surp
import surp.gce_math as gcem
from surp.yields import calc_y


import sys
sys.path.append("../../carbon_paper")
from singlezone import run_singlezone

eq_correction = 10**-0.0


def main():
    arya.style.init()
    filename, output = parse_args()
    plot_model(filename, output)


def parse_args():
    parser = argparse.ArgumentParser(description="Makes a few plots of a vice model")
    parser.add_argument("filename", help="path to surp .json model", type=str)
    parser.add_argument("-o", "--output", default="./", type=str)

    args = parser.parse_args()

    return args.filename, args.output


def plot_model(dirname, out_dir):
    pwd = os.getcwd()
    print("cd ", dirname)
    os.chdir(dirname)

    print("loading model")
    model = ViceModel.from_file("model.json")
    stars = model.stars

    print("loading yield params")
    yield_params = surp.YieldParams.from_file("yield_params.toml")
    surp.set_yields(yield_params, verbose=False)

    print("cd ", out_dir)
    os.chdir(out_dir)

    print("plotting...")
    
    print("...[o/fe]-[fe/h] stars")
    plot_ofefeh(stars)
    plt.savefig("ofefeh.pdf")
    plt.close()

    print("...[c/o]-[o/h] gas tracks")
    plot_cooh_gas(model.history)
    plt.savefig("cooh_gas.pdf")
    plt.close()


    print("...[c/o]-[o/fe] gas tracks")
    plot_coofe_gas(model.history)
    plt.savefig("coofe_gas.pdf")
    plt.close()

    print("...[c/o]-[o/h] stars")
    plot_cooh(stars)
    plt.savefig("cooh.pdf")
    plt.close()

    print("...[c/o]-[o/h] hi/lo ")
    plot_cooh_hilo(stars)
    plt.savefig("cooh_eq.pdf")
    plt.close()

    print("...[c/o]-[o/fe] stars")
    plot_coofe(stars)
    plt.savefig("coofe.pdf")
    plt.close()

    print("...[c/o]-[o/fe] slice")


    os.chdir(pwd)
    print("done")





def plot_coofe_gas(history):
    plot_tracks(history, x="MG_FE", y="AG_MG")

    plot_eq_caafe()
    plot_sz_caafe(label="singlezone", lw=2, color="k")
    plot_ssp_femg(surp.Z_SUN)

    plt.xlim(-0.2, 0.5)
    plt.ylim(-0.4, 0.2)


def plot_cooh_gas(history):
    plot_tracks(history, x="MG_H", y="AG_MG")

    plot_eq_caah()
    plt.xlim(-1.2, 0.6)
    plt.ylim(-0.4, 0.1)


def plot_cooh(df):
    sns.scatterplot(df, x="MG_H", y="AG_MG", hue="r_origin", s=0.3, alpha=1,
            legend=False, edgecolor="none", palette="arya_r", rasterized=True)

    df = sp.filter_high_alpha(df)
    df = sp.filter_high_alpha(subgiants)
    sns.kdeplot(df, x="MG_H", y="C_MG", color="k", zorder=3)

    plt.xlim(-0.8, 0.8)
    plt.ylim(-0.4, 0.2)

    plt.xlabel("[Mg/H]")
    plt.ylabel("[C/Mg]")


def plot_cooh_hilo(stars):
    df = stars[~stars.high_alpha]
    plt.scatter(df.MG_H, df.C_MG, s=0.3, alpha=1, rasterized=True)

    df = stars[stars.high_alpha]
    plt.scatter(df.MG_H, df.C_MG, s=0.3, alpha=1, rasterized=True)

    plot_eq_caah()
    plot_binned_caah(stars)

    plt.xlim(-0.8, 0.8)
    plt.ylim(-0.4, 0.2)

    plt.xlabel("[Mg/H]")
    plt.ylabel("[C/Mg]")

def plot_coofe(stars, mh0=-0.1):
    df = sp.filter_metallicity(subgiants)
    sns.kdeplot(df, x="MG_FE", y="AG_MG", color="k", zorder=3)

    df = sp.filter_metallicity(stars)
    plt.scatter(df["MG_FE"], df["AG_MG"], c=df["r_origin"], s=0.3, zorder=2, rasterized=True,)

    plot_eq_caafe()
    plot_sz_caafe(label="singlezone", lw=2, color="k")
    plot_ssp_femg(Z=gcem.MH_to_Z(mh0))

    plt.xlim(-0.1, 0.5)
    plt.ylim(-0.4, 0.3)

    plt.xlabel("[Mg/Fe]")
    plt.ylabel("[C/Mg]")


def plot_ofefeh(df):
    fig, axs = plt.subplots(2, 2, figsize=(7, 5),
        sharex="col", sharey="row", 
        gridspec_kw={"hspace": 0, "wspace": 0,
            "height_ratios": [1, 3],
            "width_ratios": [3, 1]
        }
    )

    plt.sca(axs[0, 0])
    plot_mdf(df, x="FE_H")

    plt.sca(axs[1, 0])
    sns.scatterplot(df, x="FE_H", y="MG_FE", hue="r_origin", s=0.3, alpha=1,
            legend=False, edgecolor="none", palette="arya_r", rasterized=True)

    sns.kdeplot(subgiants, x="FE_H", y="MG_FE", zorder=3, color="k")

    plt.xlim(-1, 0.5)
    plt.ylim(-0.1, 0.5)
    plt.xlabel("[Fe/H]")
    plt.ylabel("[Mg/Fe]")


    plt.sca(axs[1, 1])
    plot_mdf(df, x="MG_FE", orientation="horizontal")

    axs[0, 1].axis("off")



# ----------------- Helper functions -----------------



def plot_mdf(history, x="FE_H", histtype="step",
        density=True, range=(-1, 0.5), bins=100, **kwargs):

    hist_kwargs = dict(histtype=histtype, 
        density=density, range=range, bins=bins, **kwargs)

    plt.hist(history[x], label="model", **hist_kwargs)
    plt.hist(subgiants[x], label="data", color="k", **hist_kwargs)

    if "orientation" in kwargs:
        pass
    else:
        plt.xlabel(to_label(x))
        plt.ylabel("density")


def plot_tracks(history, x="MG_H", y="AG_MG", Rs=[4,6,8,10,12]):
    for R in Rs:
        df = history[np.isclose(history.R, R-0.05)]
        plt.plot(df[x], df[y], color="k")

    sns.scatterplot(history, x=x, y=y, hue="time", s=0.3, alpha=1,
            legend=False, edgecolor="none", palette="arya_r", rasterized=True)
    plt.xlabel(to_label(x))
    plt.ylabel(to_label(y))
    arya.Colorbar(clim=(0, 13.2), ax=plt.gca(), label="t (Gyr)", cmap="arya_r")



def plot_binned_caah(model):
    arya.medianplot(model[~model.high_alpha], "MG_H", "AG_MG", 
                    numbins=20, color="k", stat="median")

def plot_binned_caafe(model):
    arya.medianplot(model, "MG_FE", "AG_MG", numbins=20, color="k",
                   stat="median")
    
def plot_binned_caafe_slice(model, w=0, c0=-0.1):
    df = surp.plots.filter_metallicity(model, c=-0.1, w=5)
    arya.medianplot(model, "MG_FE", "AG_MG", numbins=12, color="k", 
        stat="median")



def calc_eq_caah(M_H, **kwargs):
    Zs = gcem.MH_to_Z(M_H)
    ys = calc_y(Zs)
    ymg = calc_y(Zs, "mg")

    co = gcem.abund_ratio_to_brak(ys / ymg*eq_correction, "C", "MG")
    
    return co


def plot_eq_caah(M_H =np.linspace(-0.45, 0.45, 1000),  **kwargs):
    co = calc_eq_caah(M_H)
    
    plt.plot(M_H, co, label="equilibrium", color="k", lw=2, **kwargs)
    
    
def plot_eq_caafe(**kwargs):
    M_H = np.linspace(-0.45, 0.45, 1000)
    Zs = gcem.MH_to_Z(M_H)
    yc = calc_y(Zs)
    ymg = calc_y(Zs, "mg")
    yfe = calc_y(Zs, "fe")

    co = gcem.abund_ratio_to_brak(yc / ymg * 10**-0.05, "C", "MG")
    ofe = gcem.abund_ratio_to_brak(ymg/yfe, "mg", "fe")
    
    plt.plot(ofe, co, label="equilibrium", **kwargs)
    

def plot_sz_caafe(eta=0.5, tau_sfh=15, tau_star=3.2,  **kwargs):

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sz, h = run_singlezone(eta=eta, tau_sfh=tau_sfh, tau_star=tau_star)

    plt.plot(h.O_FE, h.C_O, **kwargs)
    return sz


def plot_ssp_femg(Z, x_shift = 0, color=arya.COLORS[2],  **kwargs):
    m_c, times = vice.single_stellar_population("c", Z=Z, mstar=1)
    m_mg, times = vice.single_stellar_population("mg", Z=Z, mstar=1)
    m_fe, times = vice.single_stellar_population("fe", Z=Z, mstar=1)

    c_mg = gcem.abund_ratio_to_brak(np.array(m_c)/m_mg, "C", "MG")
    mg_fe = gcem.abund_ratio_to_brak(np.array(m_mg)/m_fe, "MG", "FE")
    plt.plot(mg_fe + x_shift, c_mg, color=color, **kwargs)



def to_label(x):
    ele1, ele2 = x.split("_")
    ele1 = ele1.title()
    ele2 = ele2.title()
    return "[%s/%s]" % (ele1, ele2)


if __name__ == "__main__":
    main()
