import vice
import pandas as pd
import numpy as np
import scipy
import random
import matplotlib.pyplot as plt
import os.path
from os.path import exists
import json
import seaborn as sns


from . import apogee_analysis as aah
from . import gas_phase_data


from .plotting_utils import legend_outside, fancy_legend
from . import plotting_utils as pluto

import arya
COLORS = arya.style.COLORS
cmap = arya.style.get_cmap()

class vice_model():
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

    Methods
    -------
    plot_stars(x, y, **kwargs)
    plot_mean_stars
    plot_gas(x, y)
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


        if plot_data:
                aah.plot_contour(x, y, xlim=xlim, zorder=2, levels=6, exclude_high_alpha=exclude_high_alpha)

        show_stars(stars, x, y, c=c, c_label=c_label, zorder=1, **kwargs)

        if xlim is not None:
            plt.xlim(xlim)


    def plot_mean_stars(self, x, y, plot_data=True, xlim=None,
            star_group="solar", ax=None, s=1, **kwargs):
        stars = self.stars[star_group]
        
        if xlim is None:
            xlim = (min(stars[x]), max(stars[x]))

        if plot_data:
            aah.plot_stars(x, y, zorder=1, ax=ax, s=s)

        pluto.plot_mean_track(stars[x], stars[y], xlim=xlim, ax=ax,  **kwargs)

        plt.xlabel(x)
        plt.ylabel(y)
        plt.xlim(xlim)

    def plot_mdf(self, x, star_group="solar", plot_data=True, xlim=None, **kwargs):
        plt.hist(self.stars[star_group][x], 50, histtype="step", density=True, range=xlim, **kwargs)
        if plot_data:
            v21 = aah.vincenzo2021()
            if x in v21.keys():
                plt.hist(v21[x], 50, histtype="step", label="V21", ls="--", density=True, color="black")

        plt.xlabel(x)
        plt.ylabel("density of stars")

    def plot_gas(self, x, y, ratio=False, filename=None, plot_data=True, **kwargs):
        self.plot_annulus_at_t(x, y, **kwargs)
        if plot_data:
            gas_phase_data.plot_all(x, y, alpha_bars=0.5)
        legend_outside()

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

    def plot_t_slices(self, x, y, xlim=None, times=[13,11,8,5,2], smooth=0.1, ax=None, legend=True):
        if ax is None:
            ax = plt.gca()

        colors = [cmap(i/5) for i in range(5)]

        for i in range(len(times)):
            t = times[i]
            c = colors[i]

            self.plot_annulus_at_t(x, y, t, label="%i Gyr" % t, ax=ax, color=c, zorder=6-i)
        if legend:
            fancy_legend(title="", ax=ax, colors=colors)

    def plot_R_slices(self, x, y, Rs=[4,6,8,10,12], ax=None, t_min=0.1, legend=True):
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

        if legend:
            fancy_legend(title="", ax=ax, colors=colors)

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

        aah.plot_coofe_contour(o_h_0, d_o_h)

        filt = stars["[o/h]"] > o_h_0 - d_o_h
        filt &= stars["[o/h]"] < o_h_0 + d_o_h
        df = stars[filt]
        show_stars(df, "[o/fe]", "[c/o]", c="age", c_label="age", s=1, zorder=2,
                **kwargs)

    def plot_cofeo(self, star_group="solar", o_h_0=-0.1, d_o_h = 0.05, **kwargs):

        stars = self.stars[star_group]

        aah.plot_coofe_contour(o_h_0, d_o_h)

        filt = stars["[o/h]"] > o_h_0 - d_o_h
        filt &= stars["[o/h]"] < o_h_0 + d_o_h
        df = stars[filt]
        df["[fe/o]"] = - np.array(df["[o/fe]"])

        show_stars(df, "[fe/o]", "[c/o]", c="age", c_label="age", s=1, zorder=2,
                **kwargs)

    def plot_mean_coofe(self, o_h_0=-0.1, d_o_h = 0.05, star_group="solar", xlim=None, plot_data=True, ax=None, **kwargs):
        if ax is None:
            ax = plt.gca()

        if plot_data:
            aah.plot_coofe(o_h_0, d_o_h)

        stars = self.stars[star_group]

        filt = stars["[o/h]"] > o_h_0 - d_o_h
        filt &= stars["[o/h]"] < o_h_0 + d_o_h
        df = stars[filt]

        pluto.plot_mean_track(df["[o/fe]"], df["[c/o]"], xlim=xlim, **kwargs)
        plt.xlabel("[o/fe]")
        plt.ylabel("[c/o]")

    def plot_mean_cofeo(self, o_h_0=-0.1, d_o_h = 0.05, star_group="solar", xlim=None, plot_data=True, ax=None, **kwargs):
        if ax is None:
            ax = plt.gca()

        if plot_data:
            aah.plot_cofeo(o_h_0, d_o_h)

        stars = self.stars[star_group]

        filt = stars["[o/h]"] > o_h_0 - d_o_h
        filt &= stars["[o/h]"] < o_h_0 + d_o_h
        df = stars[filt]

        df["[fe/o]"] = - np.array(df["[o/fe]"])
        pluto.plot_mean_track(df["[fe/o]"], df["[c/o]"], xlim=xlim, **kwargs)
        plt.xlabel("[fe/o]")
        plt.ylabel("[c/o]")


def show_at_R_z(stars, x="[fe/h]", y=None, c=None, xlim=None, ylim=None, **kwargs):
    r"""Creates a grid of plots at different R and z of show_stars

    Parameters
    ----------

    

    """
    fig, axs = plt.subplots(5, 3, sharex=True, sharey=True, figsize=(15,15), squeeze=True)
    # fig.supxlabel(x)
    # fig.supylabel(y)

    vmin = None
    vmax = None
    if c is not None:
        vmin = min(stars[c])
        vmax = max(stars[c])

    for j in range(5):
        R_min, R_max = [(3,5), (5,7), (7,9), (9,11), (11,13)][j]

        for i in range(3):
            z_min, z_max = [(0, 0.5), (0.5, 1), (1, 1.5)][i]
            filtered = sample_stars(filter_stars(stars, R_min, R_max, z_min, z_max), num=1000)

            ax = axs[j][i]
            im = show_stars(filtered, x, y, c=c, colorbar=False, fig=fig, ax=ax, vmin=vmin, vmax=vmax, **kwargs)
            ax.set(xlim=xlim,
                   ylim=ylim,
                   xlabel="",
                   ylabel=""
                  )
            if i == 0:
                ax.set(ylabel="R = %i - %i kpc" %(R_min, R_max))
            if j == 4:
                ax.set(xlabel="|z| = %1.1f - %1.1f" % (z_min, z_max))

    if c is not None:
        fig.colorbar(im, ax=axs.ravel().tolist(), label=c)



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

