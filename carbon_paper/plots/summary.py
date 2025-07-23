#!/usr/bin/env python
# coding: utf-8

# Data from many different sources. This notebook makes the last plot of
# the paper.

# TODO: need to drop duplicates between RL & CEL regions, note that RL and CEL not consistent as labeled 
# also would be nice to seperate RL by galaxy? and high z as well

# # Introduction



import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import vice




from surp import ViceModel, yields, subgiants, DATA_DIR
from surp import gce_math as gcem

import surp
import arya
from arya import COLORS


import sys
sys.path.append("..")

from singlezone import run_singlezone, exp_sfh




def to_nice(apogee_name):
    return "[" + apogee_name.title().replace("_", "/") + "]"

surp.set_yields(verbose=False)



def plot_abund_errs(df, x="O_H", y="C_O", **kwargs):
    xs = df[x].values
    ys =  df[y].values
    xerr = df[f"{x}_err"].values
    yerr = df[f"{y}_err"].values
    filt = ~np.isnan(xerr) 
    filt &= ~np.isnan(yerr)
    filt &= xerr > 0
    filt &= yerr > 0
    
    plt.errorbar(xs[filt], ys[filt], xerr=xerr[filt], yerr=yerr[filt], fmt="o", capsize=0, **kwargs)
    plt.xlabel(to_nice(x))
    plt.ylabel(to_nice(y))




def plot_sample(df, **kwargs):    
    plot_abund_errs(df, x="FE_H", y="O_FE", **kwargs)
    plt.show()
    
    plot_abund_errs(df, **kwargs)
    plt.show()
    
    plot_abund_errs(df, x="O_FE", **kwargs)
    plt.show()
    
    if "MG_FE" in df.columns:
        plot_abund_errs(df, x="O_H", y="O_MG", **kwargs)
        plot_abund_errs(df, x="MG_H", y="C_MG", **kwargs)
        plot_abund_errs(df, x="MG_FE", y="C_MG", **kwargs)
        plt.show()
                    




def calc_errs(df, idx=None):
    series = pd.Series()
    series["O_H_err"] = np.nanmean(df["O_H_err"])
    series["C_O_err"] = np.nanmean(df["C_O_err"])
    
    if idx is None:
        O_H = np.mean(df.O_H)
        C_O = np.mean(df.C_O)
        
        idx = np.argmin((df.O_H - O_H)**2 )#+ (df.C_O - C_O)**2)
        series["O_H"] = df.O_H.iloc[idx]
        series["C_O"] = df.C_O.iloc[idx]
    
    return series.to_frame().T




def plot_sample_err(df, df_err=None, color=COLORS[0], edgecolors=None, marker="*", label="", **kwargs):
    if edgecolors is None:
        edgecolors = color
        
    if df_err is None:
        df_err = calc_errs(df)
        
    plt.scatter(df["O_H"], df["C_O"], marker=marker, color=color, edgecolors=edgecolors, label=label, **kwargs)
    

    if color == "none":
        color = edgecolors

    plt.errorbar(df_err["O_H"], df_err["C_O"],  xerr=df_err.O_H_err, yerr=df_err.C_O_err,
             marker="none", ls="none", color=color, capsize=0, **kwargs)
    
    plt.xlabel("[O/H]")
    plt.ylabel("[C/O]")








all_stars = pd.read_csv("../data_analysis/amarsi19_cleaned.csv")




all_star_err = pd.DataFrame()


# split into two regemes and plot error bars
mh_cut = -0.3

low_z = all_stars[all_stars["O_H"] < mh_cut]
high_z = all_stars[all_stars["O_H"] >= mh_cut]
all_star_err = pd.concat([calc_errs(low_z), calc_errs(high_z)], ignore_index=True)
all_star_err



RL = pd.read_csv("../data_analysis/RL_combined.csv")
RL = RL[~np.isnan(RL.C_O_err)]
RL_err = calc_errs(RL)




RL_mw = RL[RL.galaxy == "MW"]
RL_mw_err = calc_errs(RL_mw)

RL = RL[RL.galaxy != "MW"]
RL_err = calc_errs(RL)




np.sort(RL.galaxy.unique())




DLA = pd.read_csv("../data_analysis/DLA_combined.csv")
DLA = DLA[~np.isnan(DLA.C_O_err)]

DLA_err = calc_errs(DLA)




DLA.sort_values("C_O")[["galaxy", "study", "C_O", "O_H"]]


CEL = pd.read_csv("../data_analysis/CEL_combined.csv")
CEL_filt = ~np.isin(CEL.galaxy, RL.galaxy.unique())
CEL_filt &= ~np.isnan(CEL.C_O_err)
CEL = CEL[CEL_filt]
CEL_err = calc_errs(CEL)




CEL.galaxy.unique()




CEL.sort_values("C_O")[["region", "galaxy", "O_H", "C_O", "study"]]




high_z = pd.read_csv("../data_analysis/high_z_cleaned.csv")
high_z = high_z[~np.isnan(high_z.C_O_err)]

high_z_err = calc_errs(high_z)





# # Fiducial model



subgiants_ha = subgiants[subgiants.high_alpha]

fiducial = ViceModel.from_file("../../models/fiducial/run/model.json")




h_today = fiducial.history[fiducial.history.time == np.max(fiducial.history.time)]
h_today = h_today[(h_today.R > 1) & (h_today.R < 15.5)].sort_values("R")
h_today




def plot_fiducial():
    plt.plot(h_today.MG_H, h_today.C_MG, label="Model (present day)", zorder=9, lw=1.5, color=arya.style.COLORS[0])

    h = fiducial.history[np.isclose(fiducial.history.R, 8 - 0.05)]
    plt.plot(h.MG_H, h.C_MG, color="k")
    

# Parameters from james et al. dwarf paper:
# 
# - $\tau_{\rm in} = 1.01 \pm 0.13\,$Gyr
# - $\eta = 8.8 \pm 0.9$
# - $\tau_{\star} = 16.1 \pm 1.3\,$Gyr
# - $\tau_{\rm end} = 5.4\pm0.3\,$Gyr
# - $y_{\rm Fe}^{\rm cc} = 7.8\pm0.4 \times 10^{-4}$
# - $y_{\rm Fe}^{\rm Ia} = 1.2\pm0.1\times 10^{-3}$
# 
# As we assume different O yields, we adjust $\eta$ accordingly. Our total O yields are 0.712e-3, so
# $$
# \frac{\eta}{
# \eta_{\rm J+22}
# } = 
# \frac{y_O}{y_{\rm O, J+22}} = \frac{0.712}{1}
# $$
# in agrement with the difference in alpha-abundance assumptions. 
# $$
# \eta = 6.2 \pm 0.7
# $$

# # Singlezone models

# ## TODO: pull these somehow from the singlezone notebook



yp = surp.YieldParams.from_file("../../models/fiducial/yield_params.toml")
surp.set_yields(yp)

y_scale = 0.6# 0.712
sz_fiducial = run_singlezone(eta=y_scale * 9.56, t_end=10.73, tau_star=26.60, tau_sfh=2.18, sfh=exp_sfh(None), mode="ifr", verbose=True)[1] # GSE

# yp = surp.YieldParams.from_file("../../models/fiducial/best/yield_params.toml")
# surp.set_yields(yp)
# 
# sz_better = run_singlezone(eta=y_scale * 9.56, t_end=10.73, tau_star=26.60, tau_sfh=2.18, sfh=exp_sfh(None), mode="ifr", verbose=True)[1] # GSE

# change dwarf parameters to
# match Wukong from James’ dwarf paper. 𝜂 = 47.99 ± 5, 𝑡end = 3.36 ± 0.5,
# 𝜏★ = 44.97 ± 7, 𝜏sfh = 3.08 ± 1


sz_models = [
        sz_fiducial,
        #sz_better
    # run_singlezone(eta=y_scale * 47.99, t_end=3.36, tau_star=44.97, tau_sfh=3.08, sfh=exp_sfh(None), mode="ifr", verbose=True)[1], # Wukong
]




from surp.yields import calc_y




MoverH = np.linspace(-5, 0.5)
Z = gcem.MH_to_Z(MoverH)

y_total = calc_y(Z)
y_agb = calc_y(Z, kind="agb")
y_cc = calc_y(Z, kind="cc")
y_ia = calc_y(Z, kind="ia")

yo = calc_y(ele="o")




def plot_sz(zorder=10):
    #singlezone
    for i in range(len(sz_models)):
        out = sz_models[i]
        if i == 0:
            label="singlezone"
        else:
            label=""
        plt.plot(out.MG_H, out.C_MG, label=label, color="k", 
                 lw=1, zorder=zorder, ls=[":", "--", "-."][i])

    plt.xlabel("[O/H]")
    plt.ylabel("[C/O]")



data_kwargs = dict(
    stat="median",
    label = r"low $\alpha$ subgiants",
    color=COLORS[4],
    err_kwargs=dict(facecolor=COLORS[4], alpha=0.0)
)

def cooh_subgiants(x="O_H", y="C_O", filt_ha=True, **kwargs):
    kwargs = dict(numbins=20, **kwargs)
    
    if filt_ha:
        df = surp.filter_high_alpha(subgiants)
    else:
        df = subgiants
        
    arya.medianplot(df, x=x, y=y, zorder=-2, **data_kwargs, **kwargs)





# # La Finale



def lower_legend_label(fig):
    plt.ylabel(r"[C/O]")

    lab = plt.xlabel(r"[O/H]")
    
    leg = fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncols=4, markerscale=2)
    box1 = leg.get_tightbbox()
    box2 = lab.get_tightbbox() 

    t1 = box1.transformed(fig.transFigure.inverted())
    t2 = box2.transformed(fig.transFigure.inverted())
    ym = (t2.y0 + t1.y1)/2


    fig.add_artist(mpl.lines.Line2D([t1.x0, t1.x1], [ym, ym], color="k", lw=0.5))




def plot_all_data():
    plot_sample_err(all_stars, all_star_err, marker="*", color=COLORS[8], label="MW stars")
    plot_sample_err(RL_mw, marker="p", color="none", edgecolors=COLORS[1], label="MW HII Regions", lw=0.5)
    
    plot_sample_err(RL, marker="d", edgecolors=COLORS[2], color="none", lw=0.5, label="HII Regions (RL)")
    plot_sample_err(CEL, CEL_err, marker="d", color=COLORS[2], label="HII regions (CEL)")

    for galaxy in RL.galaxy.unique():
        df = RL[RL.galaxy == galaxy].sort_values("O_H")
        if len(df) > 2:
            print(galaxy)
            #plt.plot(df.O_H, df.C_O, color=COLORS[2])

    plot_sample_err(high_z, high_z_err, marker="s", color=COLORS[6], label=r"high-$z$ galaxies")
    
    
    # plot_sample_err(DLA, DLA_err, marker="^", color=COLORS[3], label=r"damped Lyman$\alpha$ systems")


    cooh_subgiants()




fig = plt.figure(figsize=(7, 4))
plot_all_data()

lower_legend_label(fig)




fig = plt.figure(figsize=(7, 4))

plot_all_data()
plot_fiducial()
plot_sz()

lower_legend_label(fig)
plt.xlim(-2.6, 0.5)
plt.ylim(-1.2, 0.4)
plt.tight_layout()


plt.savefig("figures/summary.pdf")


