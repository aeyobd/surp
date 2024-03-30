import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from scipy.stats import binned_statistic
from surp import subgiants
import arya


def equal_num_hist(x, y, x_err=None, y_err=None, bins=None, ci=[16, 84]):
    """
    Calculates a histogram with equal number of points in each bin
    """

    if bins is None:
        bins = int(np.sqrt(len(x)))
    if isinstance(bins, int):
        bins = np.quantile(x, np.linspace(0, 1, bins))

    counts = binned_statistic(x, y, bins=bins, statistic="count")[0]
    xm = binned_statistic(x, x, bins=bins, statistic="median")[0]
    ym = binned_statistic(x, y, bins=bins, statistic="median")[0]
    xl = binned_statistic(x, x, bins=bins, statistic=lambda x: np.percentile(x, ci[0]))[0]
    xh = binned_statistic(x, x, bins=bins, statistic=lambda x: np.percentile(x, ci[1]))[0]
    yl = binned_statistic(x, y, bins=bins, statistic=lambda x: np.percentile(x, ci[0]))[0]
    yh = binned_statistic(x, y, bins=bins, statistic=lambda x: np.percentile(x, ci[1]))[0]

    return (xm, xl, xh), (ym, yl, yh), counts


def median_err(x, ci=[16, 84]):
    """
    Calculates the median and the error bars
    """
    return np.median(x), np.percentile(x, ci[0]), np.percentile(x, ci[1])
    
def binned_median_err(x, bins, ci=[16, 84]):
    pass


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


def filter_metallicity(df, key="MG_H", c=-0.1, w=0.05):

    filt = df[key] >= c - w
    filt &= df[key] < c + w
    return df[filt]

def filter_high_alpha(df):
    high_alpha = df["high_alpha"]
    return df[~high_alpha]


def add_scatter(df, cols=["MG_H", "C_MG", "MG_FE", "C_N", "FE_H"], sigmas=[0.03, 0.03, 0.03, 0.03, 0.03]):
    df1 = df.copy()
    N = len(df1)
    for i in range(len(cols)):
        df1[cols[i]] += np.random.normal(0, sigmas[i], N)

    return df1


def show_stars(stars, x="[fe/h]", y=None, c=None, c_label=None, s=1, alpha=1, kde=False, ax=None, fig=None, colorbar=None,vmin=None, vmax=None, x_err=0.03, y_err=0.03, **args):
    if ax is None or fig is None:
        ax = plt.gca()
        fig = plt.gcf()
        
    if kde:
        im = sns.kdeplot(stars[x]+ np.random.normal(0, x_err, len(stars[x])), ax=ax, **args)
    elif y is None:
        im = ax.hist(stars[x]+ np.random.normal(0, x_err, len(stars[x])), **args)
        ax.set_ylabel("count")
    else:
        if c is None:
            im = ax.scatter(stars[x] + np.random.normal(0, x_err, len(stars[x])), stars[y] + np.random.normal(0, y_err, len(stars[x])), s=s, vmin=vmin, vmax=vmax, alpha=alpha, **args)

        else:
            im = ax.scatter(stars[x] + np.random.normal(0, x_err, len(stars[x])), stars[y] + np.random.normal(0, y_err, len(stars[x])), c=stars[c], s=s, alpha=alpha, vmin=vmin, vmax=vmax, **args)
            if colorbar is None:
                colorbar = True
        
        ax.set_ylabel(y)
    ax.set_xlabel(x)
    
    if colorbar:
        if c_label is None:
            c_label = c
        # alt_colorbar(im, label=c_label)
        fig.colorbar(im, ax = ax, label=c_label)
    return im


def plot_annulus_at_t(vice_model, x, y, t = 13.1, dt = 0.1, c=None, R_min=3, R_max=15, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()
        
    # modified to just show values at present_day
    filt = vice_model.history["time"] > t
    filt &= vice_model.history["time"] < t+dt

    df = vice_model.history[filt].groupby("R").mean().reset_index()
    filt = df["R"] > R_min
    filt &= df["R"] < R_max

    x_values = df[filt][x]
    y_values = df[filt][y]

    if c is None:
        ax.plot(x_values, y_values, **kwargs)
    else:
        c_values = df[filt][c]
        ax.scatter(x_values, y_values, c=c_values, **kwargs)
        ax.colorbar()

    ax.set_xlabel(x)
    ax.set_ylabel(y)


def plot_annulus_history(vice_model, x, y, c=None, R_min=7, R_max=9, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()

    ave = vice_model.annulus_average(R_min, R_max)
    x_values = ave[x]
    y_values = ave[y]


    if c is None:
        ax.plot(x_values, y_values, **kwargs)
    else:
        c_values = ave[c]
        ax.scatter(x_values, y_values, c=c_values, **kwargs)
        ax.colorbar()
    ax.set_xlabel(x)
    ax.set_ylabel(y)


def plot_t_slices(vice_model, x, y, xlim=None, times=[13,11,8,5,2], smooth=0.1, ax=None):
    if ax is None:
        ax = plt.gca()

    colors = [cmap(i/5) for i in range(5)]

    for i in range(len(times)):
        t = times[i]
        c = colors[i]

        vice_model.plot_annulus_at_t(x, y, t, label="%i Gyr" % t, ax=ax, color=c, zorder=6-i)


def plot_R_slices(vice_model, x, y, Rs=[4,6,8,10,12], ax=None, t_min=0.1):
    colors = [cmap(i/5) for i in range(5)]

    if ax is None:
        ax = plt.gca()
        
    for j in range(5):
        i = (np.array([4, 6, 8, 10, 12])*10)[j]
        j0 = 2
        c = colors[j]
        
        R_min=i/10-0.5
        R_max=i/10+0.5
        plot_annulus_history(vice_model, x, y, R_min=R_min, R_max=R_max,
                label=f"{i/10:2.0f} kpc", ax=ax, color=c)

        # mark points
        ave = annulus_average(vice_model, R_min, R_max, t_min=t_min)
        t = np.round(np.arange(0.2, 13.21, 1), 2)
        x_values = ave[x][t]
        y_values = ave[y][t]
        ax.scatter(x_values, y_values, marker="x", color=c)


def annulus_average(vice_model, R_min, R_max, t_min=0.1):
    """
    Computes the average values of .history
    for each timestep for zones between R_min and R_max
    
    Attributes
    ----------
    name: ``str``
        The name of the"""
    filt = vice_model.history["R"] > R_min
    filt &= vice_model.history["R"] < R_max
    filt &= vice_model.history["time"] > t_min
    df = vice_model.history[filt]
    return df.groupby("time").mean()

