import vice
import pandas as pd
import numpy as np
import scipy
import random
import matplotlib.pyplot as plt
from os.path import exists
import pickle

import sys
sys.path.append("/users/PAS2232/aeyobd/surp")
from .vice_utils import load_model, show_stars
from ..model_scripts import multizone_sim
from . import apogee_analysis as aah
from . import gas_phase_data
from .plotting_utils import legend_outside, fancy_legend, plot_density_line, COLORS, plot_thick_line

def pickle_output(file_name, pickle_name=None, isotopic=False, overwrite=False):
    """
    Creates a vice_model object from the given vice_file and then pickles this object
    to store model information in a single file

    """
    if pickle_name is None:
        ext_loc = file_name.rfind(".")
        dir_loc = file_name.rfind("/") + 1
        name = file_name[dir_loc:ext_loc]
        pickle_name = "pickles/%s.pickle" % name



    if exists(pickle_name) and not overwrite:
        # raise ValueError("file %s exists and overwrite is not set" % pickle_name)
        print("skipping %s, file exists" % pickle_name)
        return 0


    # TODO add isotopic options
    output = load_model(file_name)
    model = vice_model(output)

    with open(pickle_name, "wb") as f:
        pickle.dump(model, f)


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

    def __init__(self, multioutput):
        """
        A class which holds a vice multioutput object for pickling

        Parameters
        ----------
        multioutput: ``vice.output``
            This is the output file recovered from a multizone simulation
            by calling ``vice.output(filename)``

        Notes
        -----
        Currently assumes a 200 zone output
        """
        self._add_zones(multioutput)
        self._add_stars(multioutput)

    @classmethod
    def from_file(cls, filename):
        """
        Given the filename of the pickled class,
        returns the unpickled class
        """

        with open(filename, "rb") as f:
            cl = pickle.load(f)
        return cl



    def _add_zones(self, multioutput):
        """
        Helper funcion while initializing the class"""
        history_cols = multioutput.zones["zone0"].history.keys()
        history_cols.append("R")
        self.history = pd.DataFrame(columns=history_cols)

        mdf_cols = multioutput.zones["zone0"].mdf.keys()
        mdf_cols.append("R")
        self.mdf = pd.DataFrame(columns=mdf_cols)

        for i in range(200):
            zone = multioutput.zones["zone%i" % i]

            df = pd.DataFrame(zone.history.todict())
            df["R"] = [i/10]*len(df)
            self.history = self.history.append(df, ignore_index=True)

            df = pd.DataFrame(zone.mdf.todict())
            df["R"] = [i/10]*len(df)
            self.mdf = self.mdf.append(df, ignore_index=True)

    def _add_stars(self, multioutput):
        """
        Helper function which both
        converts stars from vice.multioutput to 
        a pandas dataframe and samples the stars
        to weight by mass correctly"""
        self.unsampled_stars = pd.DataFrame(multioutput.stars.todict())

        n_stars = 10_000

        # filter out numerical artifacts
        max_zone = 155
        s = self.unsampled_stars[self.unsampled_stars["zone_origin"] < max_zone]
        self.stars = {}
        self.stars["all"]= sample_stars(s, n_stars)

        solar_filter = s["r_final"] > 7
        solar_filter &= s["r_final"] < 9
        solar_filter &= s["abs_z"] > 0
        solar_filter &= s["abs_z"] < 0.5
        self.stars["solar"] = sample_stars(s[solar_filter], n_stars)

        apogee_filter = s["r_final"] > 5
        apogee_filter &= s["r_final"] < 10
        apogee_filter &= s["abs_z"] > 0
        apogee_filter &= s["abs_z"] < 1
        self.stars["apogee"] = sample_stars(s[apogee_filter], n_stars)

    def plot_stars(self, x, y, c=None, c_label=None, xlim=None, star_group="all", **kwargs):
        stars = self.stars[star_group]


        aah.plot_contour(x, y, xlim=xlim, zorder=1, levels=6)

        show_stars(stars, x, y, c=c, c_label=c_label, zorder=2, **kwargs)

        if xlim is not None:
            plt.xlim(xlim)

    def plot_mean_stars(self, x, y, plot_data=True, xlim=None, star_group="all", ax=None, s=1, **kwargs):
        stars = self.stars[star_group]
        
        if xlim is None:
            xlim = (min(stars[x]), max(stars[x]))

        if plot_data:
            aah.plot_stars(x, y, zorder=1, ax=ax, s=s)

        plot_mean_track(stars[x], stars[y], xlim=xlim, ax=ax,  **kwargs)

        plt.xlabel(x)
        plt.ylabel(y)
        plt.xlim(xlim)

    def plot_mdf(self, x, star_group="all", plot_data=True, xlim=None, **kwargs):
        plt.hist(self.stars[star_group][x], 50, histtype="step", density=True, range=xlim, **kwargs)
        if plot_data:
            v21 = aah.vincenzo2021()
            if x in v21.keys():
                plt.hist(v21[x], 50, histtype="step", label="V21", ls="--", density=True, color="black")

        plt.xlabel(x)
        plt.ylabel("density of stars")

    def plot_gas(self, x, y, ratio=False, filename=None):
        self.plot_annulus_at_t(x, y)
        gas_phase_data.plot_all(x, y)
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

    def plot_coofe(self, star_group="all", o_h_0=-0.1, d_o_h = 0.05, **kwargs):

        stars = self.stars[star_group]

        aah.plot_coofe_contour(o_h_0, d_o_h)

        filt = stars["[o/h]"] > o_h_0 - d_o_h
        filt &= stars["[o/h]"] < o_h_0 + d_o_h
        df = stars[filt]
        show_stars(df, "[o/fe]", "[c/o]", c="age", c_label="age", s=1, zorder=2,
                **kwargs)

    def plot_cofeo(self, star_group="all", o_h_0=-0.1, d_o_h = 0.05):
        stars = self.stars[star_group]

        aah.plot_v21_cofeo(o_h_0, d_o_h)

        filt = stars["[o/h]"] > o_h_0 - d_o_h
        filt &= stars["[o/h]"] < o_h_0 + d_o_h
        df = stars[filt]
        df["[fe/o]"] = - np.array(df["[o/fe]"])

        show_stars(df, "[fe/o]", "[c/o]", c="age", c_label="age", s=1, zorder=2)

    def plot_mean_coofe(self, o_h_0=-0.1, d_o_h = 0.05, star_group="all", xlim=None, plot_data=True, ax=None, **kwargs):
        if ax is None:
            ax = plt.gca()

        if plot_data:
            aah.plot_coofe(o_h_0, d_o_h)

        stars = self.stars[star_group]

        filt = stars["[o/h]"] > o_h_0 - d_o_h
        filt &= stars["[o/h]"] < o_h_0 + d_o_h
        df = stars[filt]

        plot_mean_track(df["[o/fe]"], df["[c/o]"], xlim=xlim, **kwargs)
        plt.xlabel("[o/fe]")
        plt.ylabel("[c/o]")

    def plot_mean_cofeo(self, o_h_0=-0.1, d_o_h = 0.05, star_group="all", xlim=None, plot_data=True, ax=None, **kwargs):
        if ax is None:
            ax = plt.gca()

        if plot_data:
            aah.plot_v21_cofeo_scatter(o_h_0, d_o_h)

        stars = self.stars[star_group]

        filt = stars["[o/h]"] > o_h_0 - d_o_h
        filt &= stars["[o/h]"] < o_h_0 + d_o_h
        df = stars[filt]

        df["[fe/o]"] = - np.array(df["[o/fe]"])
        plot_mean_track(df["[fe/o]"], df["[c/o]"], xlim=xlim, **kwargs)
        plt.xlabel("[fe/o]")
        plt.ylabel("[c/o]")

def sample_stars(stars, num=1000):
    r"""
    Samples a population of stars while respecting mass weights

    Parameters
    ----------
    stars: ``pd.DataFrame``
        A dataframe containing stars
        Must have properties ``mass``
    num: ``int`` [default: 1000]
        The number of stars to sample

    Returns
    -------
    A np.array of the sampled parameter from stars
    """

    size = len(stars)
    result = {key: np.zeros(num) for key in stars.keys()}

    index = random.choices(np.arange(size), weights=stars["mass"], k=num)

    return stars.iloc[index].copy()


def plot_mean_track(x_vals, y_vals, bins=30, xlim=None, shade_width=False, err_mean = False, ax=None, dropna=False, **kwargs):
    """
    Plots the mean of the data as a line
    with a shaded region representing the standard deviation
    
    Parameters
    ----------
    
    x_vals: np.array like
        The x values of the data
        
    y_vals: np.array like
    bins: ``int`` [default: 50]
        The number of bins to bin the data by
    xlim: ``(int, int)`` [default: None]
        The limits of the bins of the data
        if None, uses the minimum and maximum values
    err_mean: ``bool`` [default: False]
        If true, plots the error of the mean instead
        of the standard deviation for the shaded regions
    """

    if ax is None:
        ax = plt.gca()
        
    if dropna:
        filt = ~(np.isnan(x_vals) | np.isnan(y_vals))
        x_vals = x_vals[filt]
        y_vals = y_vals[filt]
    means, bins, _ = scipy.stats.binned_statistic(x_vals, y_vals, statistic="mean", bins=bins, range=xlim)
    nums, _, _ = scipy.stats.binned_statistic(x_vals, y_vals, statistic="count", bins=bins, range=xlim)
    x_bins = 0.5*(bins[1:] + bins[:-1])
    p = ax.plot(x_bins, means, **kwargs)
    # p = plot_thick_line(x_bins, means, nums/30, ax=ax, **kwargs)
    

    if shade_width:
        std, _, _ = scipy.stats.binned_statistic(x_vals, y_vals, statistic="std", bins=bins, range=xlim)
        if err_mean:
            dy = std / np.sqrt(nums)
        else:
            dy = std
        ax.fill_between(x_bins, means - dy, means + dy, alpha=0.3, color=p[0].get_color())



    return means, bins, nums
