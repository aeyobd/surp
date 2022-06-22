import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from vice_utils import sample_stars, load_model, filter_stars, calculate_z, show_stars, R_to_zone, zone_to_R, show_at_R_z
import apogee_analysis as aah
import vice

class ModelComparer():
    def __init__(self, model_names):
        """This is a class used to create plots for comparison and model analysis"""

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
            self.stars[name] = sample_stars(s, num=10_000)
            self.solar_neighborhood_stars[name] = sample_stars(filter_stars(s, 7, 9, 0, 0.5), num=10_000)

    def plot_model_fixed_r(self, x="[o/h]", y="[c/o]"):
        for name, model in self.models.items():
            for i in np.array([4, 6, 8, 10, 12])*10:
                show_annulus_average(model, x, y, R_min=i/10-0.5, R_max=i/10+0.5, label=i/10)
            plt.legend(title="r/kpc")
            plt.xlim(-1,0.6)
            plt.title(name)
            plt.show()

    def plot_stars(self, x, y, c=None, solar_neighborhood=False):
        for name, model in self.models.items():
            if solar_neighborhood:
                s = self.solar_neighborhood_stars[name]
            else:
                s = self.stars[name]

            show_stars(s, x, y, c=c, s=0.1)
            plt.title(name)
            plt.show()

    def plot_gas(self, x, y):
        for name, model in self.models.items():
            show_annulus(model, x, y, label=name,)
        plt.legend()

    def plot_cooh(self):
        plt.figure(figsize=(8,6))
        N = len(list(self.stars.keys()))
        x_min = -0.6
        x_max = 0.4
        for i in range(N):
            name = list(self.stars.keys())[i]
            s = self.solar_neighborhood_stars[name]
            dx = 0.04
            bins = np.arange(x_min, x_max+dx, dx)
            y, yerr= means_star_value(s, "[c/o]", "[o/h]", bins)
            plt.plot(bins[:-1], y, label=name)
            plt.fill_between(bins[:-1], y-yerr, y+yerr, alpha=0.2)

        plt.legend()
        plt.xlabel("[o/h]")
        plt.ylabel("[c/o]")
        plt.xlim(x_min,x_max)

        aah.plot_apogee_cooh(c="black")


    def plot_cnfeh(self):
        plt.figure(figsize=(8,6))
        for name, s in self.stars.items():
            bins = np.arange(-0.6, 0.6, 0.02)
            y, yerr= means_star_value(s, "[c/n]", "[o/h]", bins)
            plt.plot(bins[:-1], y, label=name)
            plt.fill_between(bins[:-1], y-yerr, y+yerr, alpha=0.2)

        plt.legend()
        plt.xlabel("[fe/h]")
        plt.ylabel("[c/n]")
        aah.plot_apogee_cnfe(c="black")
        plt.xlim(-0.5, 0.5)


    def plot_cnooh(self):
        plt.figure(figsize=(8,6))
        for name, s in self.stars.items():
            cn_h = np.log10((
                aah.bracket_to_abundance(s["[c/h]"], "C") +
                aah.bracket_to_abundance(s["[n/h]"], "N"))
                / (vice.solar_z("C") + vice.solar_z("N")))
            s["[cn/h]"] = cn_h
            s["[cn/o]"] = cn_h - s["[o/h]"]
            bins = np.arange(-0.7, 0.5, 0.02)
            y, yerr= means_star_value(s, "[cn/o]", "[o/h]", bins)
            plt.plot(bins[:-1], y, label=name)
            plt.fill_between(bins[:-1], y-yerr, y+yerr, alpha=0.2)

        aah.plot_apogee_cpnoh()
        plt.xlim(-0.7, 0.5)
        plt.legend()
        plt.xlabel("[o/h]")
        plt.ylabel("[c+n/o]")





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

def cooh_age(model, name):
    for i in np.array([4, 6, 8, 10, 12])*10:
        show_annulus_average(model, "[o/h]", "[c/o]", R_min=i/10-0.5, R_max=i/10+0.5, label=i/10)
    plt.legend(title="r/kpc")
    plt.xlim(-1,0.6)
    plt.title(name)

    sf("cooh_gas_" + name)
    plt.show()

def cooh_R(model, name):
    for t in [2, 5, 8, 11, 13]:
        times = np.array(model.zones["zone0"].history["time"])
        j = int(100*t)
        j = np.arange(len(times))[times == t][0]

        y = np.zeros(155)
        x = np.zeros(155)
        R = np.arange(0, 15.5, 0.1)

        for i in range(155):
            y[i] = model.zones["zone%i" % i].history["[c/o]"][j]
            x[i] = model.zones["zone%i" % i].history["[o/h]"][j]
        plt.plot(x, y, label=t)

    plt.legend(title="t/Gry")
    #plt.xlim(-1,0.6)
    plt.title(name)
    plt.ylim(-0.7, 0.2)
    plt.xlabel("[o/h]")
    plt.ylabel("[c/o]")

    plt.show()

def cooh(model, name):
    t = 13.2
    j = int(100*t)

    j = -1

    i_min = 20
    i_max = 155
    y = np.zeros(i_max - i_min)
    x = np.zeros(i_max - i_min)

    for i in range(i_max - i_min):
        y[i] = model.zones["zone%i" % (i+i_min)].history["[c/o]"][j]
        x[i] = model.zones["zone%i" % (i+i_min)].history["[o/h]"][j]
    plt.plot(x, y, label=name)
    plt.ylim(-0.5, 0.2)
    plt.xlabel("[o/h]")
    plt.ylabel("[c/o]")

def means_star_value(stars, value, bin_name, bins):
    N = len(bins) - 1
    means = np.zeros(N)
    sds = np.zeros(N)
    for i in range(N):
        filtered_stars = stars.filter(bin_name, ">=", bins[i]).filter(bin_name, "<", bins[i + 1])
        means[i] = np.mean(filtered_stars[value])
        sds[i] = np.std(filtered_stars[value])

    return means, sds
