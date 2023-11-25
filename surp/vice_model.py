import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns

import arya
COLORS = arya.style.COLORS
cmap = arya.style.get_cmap()


class ViceModel():
    """

    Attributes
    ----------
    history: ``pd.DataFrame``
        Contains a data frame
        See vice.output.history
    mdf: ``pd.DataFrame``
        A dataframe of metallicity distribution functions by radius
    stars: ``pd.DataFrame``
    solar_neighborhood_stars
    apogee_stars
    unfiltered_stars
    """

    def __init__(self, filename):
        """
        A class which holds a vice multioutput object for pickling

        Parameters
        ----------

        Notes
        -----
        Currently assumes a 200 zone output
        """


        with open(filename, "r") as f:
            d = json.load(f)

        self.stars = pd.DataFrame(d["stars"])
        self.stars["[fe/o]"] = -self.stars["[o/fe]"]
        self.stars_unsampled = pd.DataFrame(d["stars_unsampled"])

        self.history = pd.DataFrame(d["history"])
        self.history["[fe/o]"] = -self.history["[o/fe]"]



def plot_stars(self, x, y, c=None, c_label=None, xlim=None,
        star_group="solar", exclude_high_alpha=True, plot_data = True, **kwargs):
    stars = self.stars[star_group]


    show_stars(stars, x, y, c=c, c_label=c_label, zorder=1, **kwargs)

    if xlim is not None:
        plt.xlim(xlim)


def plot_mdf(self, x, star_group="solar", plot_data=True, xlim=None, **kwargs):
    plt.hist(self.stars[star_group][x], 50, histtype="step", density=True, range=xlim, **kwargs)

    plt.xlabel(x)
    plt.ylabel("density of stars")

def plot_gas(self, x, y, ratio=False, filename=None, plot_data=True, **kwargs):
    self.plot_annulus_at_t(x, y, **kwargs)

def plot_annulus_at_t(self, x, y, t = 13.1, dt = 0.1, c=None, R_min=3, R_max=15, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()
        
    # modified to just show values at present_day
    filt = self.history["time"] > t
    filt &= self.history["time"] < t+dt

    df = self.history[filt].groupby("R").mean().reset_index()
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

def plot_annulus_history(self, x, y, c=None, R_min=7, R_max=9, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()

    ave = self.annulus_average(R_min, R_max)
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

def plot_t_slices(self, x, y, xlim=None, times=[13,11,8,5,2], smooth=0.1, ax=None):
    if ax is None:
        ax = plt.gca()

    colors = [cmap(i/5) for i in range(5)]

    for i in range(len(times)):
        t = times[i]
        c = colors[i]

        self.plot_annulus_at_t(x, y, t, label="%i Gyr" % t, ax=ax, color=c, zorder=6-i)

def plot_R_slices(self, x, y, Rs=[4,6,8,10,12], ax=None, t_min=0.1):
    colors = [cmap(i/5) for i in range(5)]

    if ax is None:
        ax = plt.gca()
        
    for j in range(5):
        i = (np.array([4, 6, 8, 10, 12])*10)[j]
        j0 = 2
        c = colors[j]
        
        R_min=i/10-0.5
        R_max=i/10+0.5
        self.plot_annulus_history(x, y, R_min=R_min, R_max=R_max,
                label=f"{i/10:2.0f} kpc", ax=ax, color=c)

        # mark points
        ave = self.annulus_average(R_min, R_max, t_min=t_min)
        t = np.round(np.arange(0.2, 13.21, 1), 2)
        x_values = ave[x][t]
        y_values = ave[y][t]
        ax.scatter(x_values, y_values, marker="x", color=c)


def annulus_average(self, R_min, R_max, t_min=0.1):
    """
    Computes the average values of self.history
    for each timestep for zones between R_min and R_max
    
    Attributes
    ----------
    name: ``str``
        The name of the"""
    filt = self.history["R"] > R_min
    filt &= self.history["R"] < R_max
    filt &= self.history["time"] > t_min
    df = self.history[filt]
    return df.groupby("time").mean()

def plot_coofe(self, star_group="solar", o_h_0=-0.1, d_o_h = 0.05, **kwargs):

    stars = self.stars[star_group]


    filt = stars["[o/h]"] > o_h_0 - d_o_h
    filt &= stars["[o/h]"] < o_h_0 + d_o_h
    df = stars[filt]
    show_stars(df, "[o/fe]", "[c/o]", c="age", c_label="age", s=1, zorder=2,
            **kwargs)

def plot_cofeo(self, star_group="solar", o_h_0=-0.1, d_o_h = 0.05, **kwargs):

    stars = self.stars[star_group]


    filt = stars["[o/h]"] > o_h_0 - d_o_h
    filt &= stars["[o/h]"] < o_h_0 + d_o_h
    df = stars[filt]
    df["[fe/o]"] = - np.array(df["[o/fe]"])

    show_stars(df, "[fe/o]", "[c/o]", c="age", c_label="age", s=1, zorder=2,
            **kwargs)




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

