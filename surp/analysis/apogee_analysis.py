import numpy as np
import pickle
import matplotlib.pyplot as plt
import vice
import pandas as pd
import seaborn as sns
from astropy.io import fits
from astropy.table import Table
import astropy.coordinates as coord
import astropy.units as u
import os
import requests
import sys


from .gce_math import *



def convert_name(x):
    """
    Helper function. Converts a name like
    [a/b] to A_B
    """
    s = x.upper()
    s = s.replace("[", "")
    s = s.replace("]", "")
    s = s.replace("/", "_")

    return s

def plot_stars(x, y, ax=None, exclude_high_alpha=True, c="black", s=1,**kwargs):
    v21 = subgiants
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    if ax is None:
        ax = plt.gca()
    x = convert_name(x)
    y = convert_name(y)
    ax.scatter(v21[x], v21[y], s=s, c=c, **kwargs)#, label="V+21")

def plot_contour(x, y, ax=None, bins=50, color="black", exclude_high_alpha=True,  **kwargs):
    v21 = subgiants
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    if ax is None:
        ax = plt.gca()
    x = convert_name(x)
    y = convert_name(y)

    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    sns.kdeplot(v21, x=x, y=y, color=color, linewidths=1, **kwargs)

def plot_cooh():
    df = subgiants
    filt = ~df["high_alpha"]
    df = df[filt]
    plt.scatter(df["MG_H"], df["C_MG"], color="k", s=1, alpha=0.1)

def plot_coofe(c=-0.1, w=0.05, s=1, alpha=0.1, color="black", **kwargs):
    v21 = subgiants

    filt = v21["MG_H"] > c - w
    filt &= v21["MG_H"] < c + w
    df=  v21[filt]
    plt.scatter(df["MG_FE"], df["C_MG"], color=color, s=s, alpha=alpha, **kwargs)

def plot_mean_coofe(c=-0.1, w=0.05, s=1, color="black", **kwargs):
    v21 = subgiants

    filt = v21["MG_H"] > c - w
    filt &= v21["MG_H"] < c + w
    df=  v21[filt]
    pluto.plot_mean_track(df["MG_FE"], df["C_MG"], color="black", **kwargs)

def plot_cofeo(c=-0.1, w=0.05, s=1, alpha=0.1, **kwargs):
    v21 = subgiants

    filt = v21["MG_H"] > c - w
    filt &= v21["MG_H"] < c + w
    df=  v21[filt]
    plt.scatter(-df["MG_FE"], df["C_MG"], color="black", s=s, alpha=alpha, **kwargs)

def plot_coofe_contour(c=-0.1, w=0.05):
    v21 = subgiants

    filt = v21["MG_H"] > c - w
    filt &= v21["MG_H"] < c + w
    df=  v21[filt]
    sns.kdeplot(df, x="MG_FE", y="C_MG", color="black", linewidths=1)



def plot_v21(x, y, ax=None, exclude_high_alpha=True, s=1,**kwargs):
    v21 = vincenzo2021()
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    if ax is None:
        ax = plt.gca()
    ax.scatter(v21[x], v21[y], s=s, c="black", **kwargs)#, label="V+21")

def plot_v21_contour(x, y, bins=50,exclude_high_alpha=True,  **kwargs):
    v21 = vincenzo2021()
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]
    sns.kdeplot(v21, x=x, y=y, color="black", linewidths=1, **kwargs)#, label="V+21")

def plot_v21_coofe(c=-0.1, w=0.05):
    v21 = vincenzo2021()

    filt = v21["[o/h]"] > c - w
    filt &= v21["[o/h]"] < c + w
    df = v21[filt]
    df["[o/fe]"] = df["[o/h]"] - df["[fe/h]"]
    sns.kdeplot(df, x="[o/fe]", y="[c/o]", color="black", linewidths=1)

def plot_v21_cofeo(c=-0.1, w=0.05):
    v21 = vincenzo2021()

    filt = v21["[o/h]"] > c - w
    filt &= v21["[o/h]"] < c + w
    df = v21[filt]
    df["[o/fe]"] = df["[o/h]"] - df["[fe/h]"]
    df["[fe/o]"] = -df["[o/fe]"]
    sns.kdeplot(df["[fe/o]"], df["[c/o]"], color="black", linewidths=1)

def plot_v21_coofe_scatter(c=-0.1, w=0.05):
    v21 = vincenzo2021()

    filt = v21["[o/h]"] > c - w
    filt &= v21["[o/h]"] < c + w
    df=  v21[filt]
    df["[o/fe]"] = df["[o/h]"] - df["[fe/h]"]
    df["[fe/o]"] = -df["[o/fe]"]
    plt.scatter(df["[o/fe]"], df["[c/o]"], color="black", s=1)

def plot_v21_cofeo_scatter(c=-0.1, w=0.05):
    v21 = vincenzo2021()

    filt = v21["[o/h]"] > c - w
    filt &= v21["[o/h]"] < c + w
    df=  v21[filt]
    df["[o/fe]"] = df["[o/h]"] - df["[fe/h]"]
    df["[fe/o]"] = -df["[o/fe]"]
    plt.scatter(df["[fe/o]"], df["[c/o]"], color="black", s=1)

def calc_mean(x, y, bins=50, xlim=None):
    if type(bins) is int:
        if xlim is None:
            xlim = (min(x), max(x))
        bins = np.linspace(xlim[0], xlim[1], 50)

    N = len(bins) - 1
    means = np.zeros(N)
    sds = np.zeros(N)
    counts = np.zeros(N)

    for i in range(N):
        filt = y[(x >= bins[i]) & (x < bins[i+1])]
        means[i] = np.mean(filt)
        sds[i] = np.std(filt)
        counts[i] = len(filt)

    return bins, means, sds, counts

def calc_mean_v21(x, y, bins=50, xlim=None, exclude_high_alpha=True):
    v21 = vincenzo2021()
    if exclude_high_alpha:
        v21 = v21[~v21["high_alpha"]]

    if type(bins) is int:
        if xlim is None:
            xlim = (min(v21[x]), max(v21[x]))
        bins = np.linspace(xlim[0], xlim[1], 50)

    N = len(bins) - 1
    means = np.zeros(N)
    sds = np.zeros(N)
    counts = np.zeros(N)

    for i in range(N):
        filt = v21[(v21[x] >= bins[i]) & (v21[x] < bins[i+1])]
        means[i] = np.mean(filt[y])
        sds[i] = np.std(filt[y])
        counts[i] = len(filt)

    return bins, means, sds, counts

def plot_mean_v21(x, y, ax=None, bins=50, exclude_high_alpha=True, xlim=None, ylim=None, **kwargs):
    if ax is None:
        ax = plt.gca()

    bins, means, sds, counts = calc_mean_v21(x, y, bins, xlim, exclude_high_alpha)

    ax.plot(bins[:-1], means, label="V21", color="black")
    # ax.fill_between(bins[:-1], means-sds, means+sds, color="black", label="V+21")

    return means, sds
    # ax.plot(bins[:-1], means-sds, color="black", ls=":")
    # ax.plot(bins[:-1], means+sds, color="black", ls=":")


    

def plot_skillman20_cooh(**kwargs):
    c_o = [-0.04, -0.08, -0.31, -0.39,-.28,-.34,-.30,-.25,-.63,-.47]
    c_o_err = [.07,.04,.12,.19,.12,.11,.09,.17,.50,.46]
    o_h = [8.57,8.57,8.48,8.45,8.43,8.39,8.42,8.35,8.26,8.14]
    o_h_err = [0.02,0.01,.02,.05,.01,.02,.01,.01,.03,.03]
    plt.errorbar(log_to_bracket(o_h, "o") - 12, log_to_bracket(c_o, "c", "o"), yerr=c_o_err, xerr = o_h_err, fmt="o", **kwargs)

def plot_skillman20_cnoh(**kwargs):
    o_h = [8.57,8.57,8.48,8.45,8.43,8.39,8.42,8.35,8.26,8.14]
    o_h_err = [0.02,0.01,.02,.05,.01,.02,.01,.01,.03,.03]
    c_n = [.92,.93,.69,.81,.90,.81,.83,.88,.70,.90]
    c_n_err = [.08,.05,.13,.21,.13,.13,.10,.18,.50,.50]
    plt.errorbar(log_to_bracket(o_h, "o") - 12, log_to_bracket(c_n, "c", "n"), yerr=c_n_err, xerr = o_h_err, fmt="o", **kwargs)




subgiants = read_subgiants()
