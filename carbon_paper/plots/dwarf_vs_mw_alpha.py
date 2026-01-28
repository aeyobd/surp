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



def plot_fiducial():
    #plt.plot(h_today.FE_H, h_today.MG_FE, label="model (present day)", zorder=9, lw=1.5, color=arya.style.COLORS[0])

    h = fiducial.history[np.isclose(fiducial.history.R, 8 - 0.05)]
    plt.plot(h.FE_H, h.MG_FE, color="k", label="model (solar zone)")
    

yp = surp.YieldParams.from_file("../../models/fiducial/yield_params.toml")
surp.set_yields(yp)

y_scale = 0.6# 0.712
sz_fiducial = run_singlezone(eta=y_scale * 9.56, t_end=10.73, tau_star=26.60, tau_sfh=2.18, sfh=exp_sfh(None), mode="ifr", verbose=True)[1] # GSE


sz_models = [
        sz_fiducial,
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
            label="GSE (singlezone)"
        else:
            label=""
        plt.plot(out.FE_H, out.MG_FE, label=label, color="k", 
                 lw=1, zorder=zorder, ls=[":", "--", "-."][i])

    plt.xlabel("[Fe/H]")
    plt.ylabel("[Mg/Fe]")



data_kwargs = dict(
    stat="median",
    label = r"low-$\alpha$ subgiants",
    color=COLORS[4],
    err_kwargs=dict(facecolor=COLORS[4], alpha=0.0)
)

def cooh_subgiants(x="FE_H", y="MG_FE", filt_ha=True, **kwargs):
    kwargs = dict(numbins=20, **kwargs)
    
    if filt_ha:
        df = surp.filter_high_alpha(subgiants)
    else:
        df = subgiants
        
    arya.medianplot(df, x=x, y=y, zorder=-2, **data_kwargs, **kwargs)




fiducial = ViceModel.from_file("../../models/fiducial/run/model.json")



fig = plt.figure()
plt.scatter(subgiants["FE_H"], subgiants["MG_FE"], color=COLORS[2], s=0.5, lw=0, label="subgiants")
plot_fiducial()
plot_sz()
plt.legend(loc="lower left")
plt.ylim(-0.2, 0.6)
plt.xlim(-3.5, 0.5)
plt.savefig("figures/dwarf_alpha_fe.pdf")

