import vice
import pandas as pd
import numpy as np
import scipy
import random
import matplotlib.pyplot as plt
import os.path
from os.path import exists
import json

from .vice_utils import load_model, show_stars
from ..simulation import multizone_sim
from . import apogee_analysis as aah
from .import gas_phase_data
from .plotting_utils import legend_outside, fancy_legend, plot_density_line, COLORS, plot_thick_line
from . import plotting_utils as pluto


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

        self.stars = d["stars"]
        for name, val in self.stars.items():
            self.stars[name] = pd.DataFrame(val)

        self.history = pd.DataFrame(d["history"])



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

    def plot_gas(self, x, y, ratio=False, filename=None, **kwargs):
        self.plot_annulus_at_t(x, y, **kwargs)
        gas_phase_data.plot_all(x, y, alpha_bars=0.5)
        legend_outside()

    def plot_annulus_at_t(self, x, y, t = 13, dt = 0.1, c=None, R_min=0, R_max=15.4, ax=None, **kwargs):
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

    def plot_t_slices(self, x, y, xlim=None, times=[2,5,8,11,13], ax=None, legend=True):
        if ax is None:
            ax = plt.gca()

        colors = COLORS[:4] + ["k"]

        for i in range(len(times)):
            t = times[i]
            c = colors[i]

            self.plot_annulus_at_t(x, y, t, label="%i" % t, ax=ax, color=c)
        if legend:
            fancy_legend(title="t/Gyr", ax=ax, colors=colors)

    def plot_R_slices(self, x, y, Rs=[4,6,8,10,12], ax=None, legend=True):
        for j in range(5):
            i = (np.array([4, 6, 8, 10, 12])*10)[j]
            j0 = 2
            if j == j0:
                c = "k"
            elif j<j0:
                c = COLORS[j]
            else:
                c = COLORS[j-1]

            self.plot_annulus_history(x, y, R_min=i/10-0.5, R_max=i/10+0.5, label=i/10, ax=ax, color=c)
        if legend:
            fancy_legend(title="r/kpc", ax=ax, colors=COLORS[:2] + ["k"] + COLORS[2:])

    def annulus_average(self, R_min, R_max):
        """
        Computes the average values of self.history
        for each timestep for zones between R_min and R_max
        
        Attributes
        ----------
        name: ``str``
            The name of the"""
        filt = self.history["R"] > R_min
        filt &= self.history["R"] < R_max
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

