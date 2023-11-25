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



def vice_to_apogee_name(x):
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
    df = subgiants
    if exclude_high_alpha:
        df = df[~df["high_alpha"]]
    if ax is None:
        ax = plt.gca()
    x = vice_to_apogee_name(x)
    y = vice_to_apogee_name(y)
    ax.scatter(df[x], df[y], s=s, c=c, **kwargs)#, label="V+21")

def plot_contour(x, y, ax=None, bins=50, color="black", exclude_high_alpha=True,  **kwargs):
    df = subgiants
    if exclude_high_alpha:
        df = df[~df["high_alpha"]]
    if ax is None:
        ax = plt.gca()
    x = vice_to_apogee_name(x)
    y = vice_to_apogee_name(y)

    if exclude_high_alpha:
        df = df[~df["high_alpha"]]
    sns.kdeplot(df, x=x, y=y, color=color, linewidths=1, **kwargs)

def plot_cooh():
    df = subgiants
    filt = ~df["high_alpha"]
    df = df[filt]
    plt.scatter(df["MG_H"], df["C_MG"], color="k", s=1, alpha=0.1)

def plot_coofe(c=-0.1, w=0.05, s=1, alpha=0.1, color="black", **kwargs):
    df = subgiants

    filt = df["MG_H"] > c - w
    filt &= df["MG_H"] < c + w
    df=  df[filt]
    plt.scatter(df["MG_FE"], df["C_MG"], color=color, s=s, alpha=alpha, **kwargs)

def plot_mean_coofe(c=-0.1, w=0.05, s=1, color="black", **kwargs):
    df = subgiants

    filt = df["MG_H"] > c - w
    filt &= df["MG_H"] < c + w
    df=  df[filt]
    pluto.plot_mean_track(df["MG_FE"], df["C_MG"], color="black", **kwargs)

def plot_cofeo(c=-0.1, w=0.05, s=1, alpha=0.1, **kwargs):
    df = subgiants

    filt = df["MG_H"] > c - w
    filt &= df["MG_H"] < c + w
    df=  df[filt]
    plt.scatter(-df["MG_FE"], df["C_MG"], color="black", s=s, alpha=alpha, **kwargs)

def plot_coofe_contour(c=-0.1, w=0.05):
    df = subgiants

    filt = df["MG_H"] > c - w
    filt &= df["MG_H"] < c + w
    df=  df[filt]
    sns.kdeplot(df, x="MG_FE", y="C_MG", color="black", linewidths=1)


