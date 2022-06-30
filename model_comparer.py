import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from vice_utils import sample_stars, load_model, filter_stars, calculate_z, show_stars, R_to_zone, zone_to_R, show_at_R_z
import apogee_analysis as aah
import vice
import gas_phase_data
from plotting import fig_saver

class ModelComparer():
    def __init__(self, model_names, sf=None):
        """This is a class used to create plots for comparison and model analysis"""
        if sf is None:
            self.sf = fig_saver("figures")
        else:
            self.sf=sf

        # import surp
        self.models = {}
        output_dir = "output/"
        
        for name in model_names:
            self.models[name] = load_model(output_dir + name)

        self.calc_stars()

    def calc_stars(self):
        max_zone = 155
        self.stars = {}
        self.solar_neighborhood_stars = {}

        for name, model in self.models.items():
            # remove numerical artifacts
            s = model.stars.filter("zone_origin", "<", max_zone)

            # add C+N column
            cn_h = np.log10((
                aah.bracket_to_abundance(np.array(s["[c/h]"]), "C") +
                aah.bracket_to_abundance(np.array(s["[n/h]"]), "N"))
                / (vice.solar_z("C") + vice.solar_z("N")))
            s["[c+n/h]"] = cn_h
            s["[c+n/o]"] = cn_h - s["[o/h]"]

            self.stars[name] = sample_stars(s, num=10_000)
            self.solar_neighborhood_stars[name] = sample_stars(filter_stars(s, 7, 9, 0, 0.5), num=10_000)

    def plot_model_fixed_r(self, x="[o/h]", y="[c/o]", filename=None):
        for name, model in self.models.items():
            for i in np.array([4, 6, 8, 10, 12])*10:
                show_annulus_average(model, x, y, R_min=i/10-0.5, R_max=i/10+0.5, label=i/10)
            plt.legend(title="r/kpc")
            plt.xlim(-1,0.6)
            plt.title(name)
            if filename is not None:
                self.sf(filename)
            plt.show()

    def plot_model_fixed_t(self, x_name="[o/h]", y_name="[c/o]", xlim=None, ylim=None, filename=None):
        for name, model in self.models.items():
            for t in [2, 5, 8, 11, 13]:
                times = np.array(model.zones["zone0"].history["time"])
                j = int(100*t)
                j = np.arange(len(times))[times == t][0]

                y = np.zeros(155)
                x = np.zeros(155)
                R = np.arange(0, 15.5, 0.1)

                for i in range(155):
                    y[i] = model.zones["zone%i" % i].history[y_name][j]
                    x[i] = model.zones["zone%i" % i].history[x_name][j]
                plt.plot(x, y, label=t)

            plt.legend(title="t/Gry")
            plt.title(name)
            plt.xlabel(x_name)
            plt.ylabel(y_name)

            if xlim is not None:
                plt.xlim(xlim)
            if ylim is not None:
                plt.ylim(ylim)

            if filename is not None:
                self.sf(filename)
            plt.show()

    def plot_stars(self, x, y, c=None, solar_neighborhood=False, xlim=None, ylim=None, filename=None):
        for name, model in self.models.items():
            if solar_neighborhood:
                s = self.solar_neighborhood_stars[name]
            else:
                s = self.stars[name]

            v21 = aah.vincenzo2021()

            if x in v21.keys() and y in v21.keys():
                aah.plot_mean_v21(x, y, xlim=xlim, zorder=1, levels=6)

            show_stars(s, x, y, c=c, s=0.1, zorder=2)
            plt.title(name)

            if xlim is not None:
                plt.xlim(xlim)
            if ylim is not None:
                plt.ylim(ylim)

            if filename is not None:
                self.sf(filename)
            plt.show()


    def plot_gas(self, x, y, filename=None):
        for name, model in self.models.items():
            show_annulus(model, x, y, label=name,)
        gas_phase_data.plot_all(x, y)
        plt.legend()

        if filename is not None:
            self.sf(filename)

        plt.show()


    def plot_mdf(self, x, filename=None):
        for name, st in self.stars.items():
            plt.hist(st[x], 50, histtype="step", label=name, density=True)

        v21 = aah.vincenzo2021()
        if x in v21.keys():
            plt.hist(v21[x], 50, histtype="step", label="V21", ls="--", density=True, color="black")

        plt.legend(loc="upper left")
        plt.xlabel(x)
        plt.ylabel("density of stars")

        if filename is not None:
            self.sf(filename)

        plt.show()

    def plot_all_mean_stars(self, filename=None):
        fig, axs = plt.subplots(2, 2, figsize=(15, 9))
        for n in range(4):
            i = n % 2
            j = n // 2

            ax = axs[i][j]
            x = ["[o/h]", "[o/h]", "[fe/h]", "[o/h]"][n]
            y = ["[c/o]", "[n/o]", "[c/n]", "[c+n/o]"][n]
            self.plot_mean_stars(x, y, xlim=(-0.6, 0.4), ax=ax)
        if filename is not None:
            self.sf(filename)
        plt.show()

    def plot_mean_stars(self, x_name, y_name, xlim=None, nbins=50, filename=None, ax=None):
        plt.figure(figsize=(8,6))
        N = len(list(self.stars.keys()))
        
        if ax is None:
            ax = plt.gca()


        names = list(self.stars.keys())
        if xlim is None:
            xlim = (min(self.stars[names[0]][x_name]), max(self.stars[names[0]][x_name]))

        v21 = aah.vincenzo2021()
        if x_name in v21.keys() and y_name in v21.keys():
            aah.plot_v21(x_name, y_name, zorder=1, ax=ax)

        for i in range(N):
            name = names[i]
            s = self.solar_neighborhood_stars[name]
            bins = np.linspace(xlim[0], xlim[1], nbins)
            y, yerr= means_star_value(s, y_name, x_name, bins)
            ax.plot(bins[:-1], y, label=name, zorder=3)
            ax.fill_between(bins[:-1], y-yerr, y+yerr, alpha=0.2, zorder=2)

        ax.legend()
        ax.set(xlabel=x_name, ylabel=y_name)
        ax.set_xlim(xlim)

        if filename is not None:
            self.sf(filename)
        if ax is None:
            plt.show()



# static methods
# --------------------------------------------------------------
def annulus_average(output, name, zone_min, zone_max):
    # not the most useful, for time tracks
    return np.average(np.array([output.zones["zone%i" % i].history[name]
                                for i in range(zone_min, zone_max)]
                              ),
                      axis=0)

def show_annulus_average(output, x, y, c=None, R_min=7, R_max=9, **kwargs):
    zone_min = R_to_zone(R_min)
    zone_max = R_to_zone(R_max)
    x_values = annulus_average(output, x, zone_min, zone_max)
    y_values = annulus_average(output, y, zone_min, zone_max)

    if c is None:
        plt.plot(x_values, y_values, **kwargs)
    else:
        c_values = annulus_average(output, c, zone_min, zone_max)
        plt.scatter(x_values, y_values, c=c_values, **kwargs)
        plt.colorbar()
    plt.xlabel(x)
    plt.ylabel(y)

def show_annulus(output, x, y, c=None, R_min=0, R_max=15.4, **kwargs):
    # modified to just show values at present_day
    zone_min = R_to_zone(R_min)
    zone_max = R_to_zone(R_max)
    x_values = [output.zones["zone%i" % i].history[x][-1] for i in range(zone_min, zone_max)]
    y_values = [output.zones["zone%i" % i].history[y][-1] for i in range(zone_min, zone_max)]

    if c is None:
        plt.plot(x_values, y_values, **kwargs)
    else:
        c_values = [output.zones["zone%i" % i].history[c][-1] for i in range(zone_min, zone_max)]
        plt.scatter(x_values, y_values, c=c_values, **kwargs)
        plt.colorbar()
    plt.xlabel(x)
    plt.ylabel(y)

# def cooh_age(model, name):
#     for i in np.array([4, 6, 8, 10, 12])*10:
#         show_annulus_average(model, "[o/h]", "[c/o]", R_min=i/10-0.5, R_max=i/10+0.5, label=i/10)
#     plt.legend(title="r/kpc")
#     plt.xlim(-1,0.6)
#     plt.title(name)
# 
#     sf("cooh_gas_" + name)
#     plt.show()
# 
# def cooh_R(model, name):
#     for t in [2, 5, 8, 11, 13]:
#         times = np.array(model.zones["zone0"].history["time"])
#         j = int(100*t)
#         j = np.arange(len(times))[times == t][0]
# 
#         y = np.zeros(155)
#         x = np.zeros(155)
#         R = np.arange(0, 15.5, 0.1)
# 
#         for i in range(155):
#             y[i] = model.zones["zone%i" % i].history["[c/o]"][j]
#             x[i] = model.zones["zone%i" % i].history["[o/h]"][j]
#         plt.plot(x, y, label=t)
# 
#     plt.legend(title="t/Gry")
#     #plt.xlim(-1,0.6)
#     plt.title(name)
#     plt.ylim(-0.7, 0.2)
#     plt.xlabel("[o/h]")
#     plt.ylabel("[c/o]")
# 
#     plt.show()
# 
# def cooh(model, name):
#     t = 13.2
#     j = int(100*t)
# 
#     j = -1
# 
#     i_min = 20
#     i_max = 155
#     y = np.zeros(i_max - i_min)
#     x = np.zeros(i_max - i_min)
# 
#     for i in range(i_max - i_min):
#         y[i] = model.zones["zone%i" % (i+i_min)].history["[c/o]"][j]
#         x[i] = model.zones["zone%i" % (i+i_min)].history["[o/h]"][j]
#     plt.plot(x, y, label=name)
#     plt.ylim(-0.5, 0.2)
#     plt.xlabel("[o/h]")
#     plt.ylabel("[c/o]")

def means_star_value(stars, value, bin_name, bins):
    N = len(bins) - 1
    means = np.zeros(N)
    sds = np.zeros(N)
    for i in range(N):
        filtered_stars = stars.filter(bin_name, ">=", bins[i]).filter(bin_name, "<", bins[i + 1])
        means[i] = np.mean(filtered_stars[value])
        sds[i] = np.std(filtered_stars[value])

    return means, sds
