import toml
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from dataclasses import dataclass

from corner import corner

import arya
import surp.gce_math as gcem

import os

current_dir = os.path.dirname(os.path.abspath(__file__))

@dataclass
class MCMCResult:
    params: dict
    labels: list
    all_labels: list
    samples: pd.DataFrame
    afe: pd.DataFrame
    ah: pd.DataFrame


    @classmethod
    def from_file(cls, modelname, y0=None, y_a=None, zeta_a=None, burn=0):
        modeldir = current_dir + "/../models/perturbations/mc_analysis/" + modelname + "/"
    
        with open(modeldir + "params.toml", "r") as f:
            params = toml.load(f)
    
    
        samples = pd.read_csv(modeldir + "mcmc_samples.csv")
        filt = samples.iteration >= burn
        samples = samples[filt]

        all_labels = [k for k, v in params.items() if type(v) == dict]
        filt_const = [(v["prior"] != "Normal" or v["prior_args"][1] != 0.0) for k, v in params.items() if type(v) == dict]
        labels = np.array(all_labels)[filt_const]
        
        for label in np.array(all_labels)[~np.array(filt_const)]:
            print("adding ", label)
            samples[label] = params[label]["prior_args"][0]
            
        print("length of samples = ", len(samples))

        
        if y0 is not None:
            ya = samples["alpha"] * y0
            yt = ya + samples["y0_cc"] * 1e-3
            f = ya / yt
            samples["f_agb"] = f
            samples["y_tot"] = yt
            
        if y_a is not None:
            ya = samples["alpha"] * y_a
            yt = ya + samples["y0_cc"] * 1e-3
            f = ya / yt
            samples["f_agb_a"] = f
            samples["y_tot_a"] = yt
            samples["zeta1_a"] = samples["zeta_cc"] * 1e-3 + samples["alpha"] * zeta_a
        
        afe = pd.read_csv(modeldir + "mg_fe_binned.csv")
        ah = pd.read_csv(modeldir + "mg_h_binned.csv")
        labels = [k for k, v in params.items() if type(v) == dict and (v["prior"] != "Normal" or v["prior_args"][1] != 0.0)]

            
        all_labels = [k for k, v in params.items() if type(v) == dict ]
    
        return cls(params=params, labels=labels, all_labels=all_labels, afe=afe, ah=ah, samples=samples)


    @classmethod
    def from_test_file(cls, modelname, y0=None, y_a=1e-3, zeta_a=-1e-3, burn=0):
        modeldir = "./mcmc_samples/"
    
        samples = pd.read_csv(modeldir + f"{modelname}.csv")
        print("length of samples = ", len(samples))
        
        if y0 is not None:
            ya = samples["alpha"] * y0
            yt = ya + samples["zeta0"] * 1e-3
            f = ya / yt
            samples["f_agb"] = f
            samples["y_tot"] = yt
            
        if y_a is not None:
            ya = samples["alpha"] * y_a
            yt = ya + samples["zeta0"] * 1e-3
            f = ya / yt
            samples["f_agb_a"] = f
            samples["y_tot_a"] = yt
            samples["zeta1_a"] = samples["zeta1"] * 1e-3 + samples["alpha"] * zeta_a

        ah = pd.read_csv(modeldir + "ah_binned.csv")
        ah["_x"] = ah.x
        afe = pd.read_csv(modeldir + "afe_binned.csv")
        afe["_x"] = afe.x
        labels = ["alpha", "zeta0", "zeta1", "zeta2"]
    
    
        return cls(params={}, labels=labels, all_labels=labels, afe=afe, ah=ah, samples=samples)


    def print_stats(self):
        result = self
        print("parameter\t med\t 16th\t 84th\t0.1th\t99.9th")
        for name in result.labels:
            col = result.samples[name]
            m = np.median(col)
            l, h, ll, hh = np.quantile(col, [0.16, 0.84, 0.001, 0.999])
            print(f"{name:8s}\t{m:6.3f}\t{l-m:6.3f}\t+{h-m:5.3f}\t{ll-m:5.3f}\t+{hh-m:5.3f}")

        if "sigma_int" in result.samples.keys():
            col = result.samples.sigma_int
            m = np.median(col)
            l, h, ll, hh = np.quantile(col, [0.16, 0.84, 0.001, 0.999])
            print(f"{'sigma_int':8s}\t{m:6.3f}\t{l-m:6.3f}\t+{h-m:5.3f}\t{ll-m:5.3f}\t+{hh-m:5.3f}")



        for name in result.all_labels:
            if name not in result.labels:
                m = np.median(result.samples[name])
                print(f"{name:8s}\t{m:6.3f}")

    def plot_corner(self, labels=None, **kwargs):
        """
        Plot the corner plot of the samples

        Calls the corner.corner function with the samples from the MCMCResult object
        """
        result = self
        if labels is not None:
            plot_labels = [labels[l] for l in result.all_labels]
        else:
            plot_labels = result.labels
        labels = result.labels

        if "sigma_int" in result.samples.keys():
            labels = labels.copy()
            labels.append("sigma_int")
            plot_labels = plot_labels.copy()
            plot_labels.append(r"$\sigma_{\rm int}$")

        corner(result.samples[labels],  
               show_titles=True, 
               quantiles=[0.16, 0.5, 0.84], 
               labels=plot_labels,
               **kwargs)
        return 


def plot_samples_caah(mcmc_result, alpha=None, skip=10, color="black"):
    ah = mcmc_result.ah
    labels = mcmc_result.all_labels
    samples = mcmc_result.samples[::skip]


    if alpha is None:
        alpha = 1 / len(samples)**(1/3) / 10
    
    for l, sample in samples.iterrows():
        y = np.sum([sample[label] * ah[label] for label in labels], axis=0)

        plt.plot(ah._x, gcem.abund_ratio_to_brak(y, "c", "mg") , color=color, alpha=alpha, rasterized=True)
    
    plt.xlabel("[Mg/H]")
    plt.ylabel("[C/Mg]")


def plot_sample(sample, ah, labels, **kwargs):
    y = np.sum([sample[label] * ah[label] for label in labels], axis=0)
    plt.plot(ah._x, gcem.abund_ratio_to_brak(y, "c", "mg") , **kwargs )


def plot_samples_caah_mean(mcmc_result,plot_obs=True, **kwargs):
    ah = mcmc_result.ah
    labels = mcmc_result.all_labels

    sample = np.mean(mcmc_result.samples, axis=0)
    y = np.sum([sample[label] * ah[label] for label in labels], axis=0)

    plt.plot(ah._x, gcem.abund_ratio_to_brak(y, "c", "mg") , **kwargs )

    
    plt.xlabel("[Mg/H]")
    plt.ylabel("[C/Mg]")

def plot_obs_caah(mcmc_result, **kwargs):
    ah = mcmc_result.ah

    yerr = ah.obs_err / ah.obs / np.log(10) / np.sqrt(ah.obs_counts)
    y = gcem.abund_ratio_to_brak(ah.obs, "c", "mg") 
    plt.errorbar(ah._x, y, yerr=yerr, fmt="o", **kwargs)


def plot_samples_caafe(mcmc_result, alpha=None, skip=10, color="black", **kwargs):
    ah = mcmc_result.afe
    labels = mcmc_result.all_labels
    samples = mcmc_result.samples[::skip]
    
    if alpha is None:
        alpha = 1 / len(samples)**(1/3) / 10

    for l, sample in samples.iterrows():
        y = np.sum([sample[label] * ah[label] for label in labels], axis=0)

        plt.plot(ah._x, gcem.abund_ratio_to_brak(y, "c", "mg"), color=color, alpha=alpha, rasterized=True, **kwargs)
    plt.xlabel("[Mg/Fe]")
    plt.ylabel("[C/Mg]")

def plot_obs_caafe(mcmc_result, **kwargs):
    ah = mcmc_result.afe

    yerr = ah.obs_err / ah.obs / np.log(10) / np.sqrt(ah.obs_counts)
    y = gcem.abund_ratio_to_brak(ah.obs, "c", "mg") 
    plt.errorbar(ah._x, y, yerr=yerr, fmt="o", **kwargs)


def plot_samples_caafe_mean(mcmc_result, plot_obs=True, **kwargs):
    ah = mcmc_result.afe
    labels = mcmc_result.all_labels
    
    sample = np.mean(mcmc_result.samples, axis=0)

    y = np.sum([sample[label] * ah[label] for label in labels], axis=0)

    plt.plot(ah._x, gcem.abund_ratio_to_brak(y, "c", "mg"), **kwargs)

    plt.xlabel("[Mg/Fe]")
    plt.ylabel("[C/Mg]")


def plot_fagb_hist(results):
    f = results.samples["f_agb_a"]
    plt.hist(f)
    plt.xlabel(r"$f_{\rm AGB}$")
    plt.ylabel("counts")
    l, m, h = np.quantile(f, [0.16, 0.5, 0.84])
    plt.title(f"${m:0.3f}_{{-{m-l:0.3f}}}^{{+{h-m:0.3f}}}$")

def plot_yields(result):
    for label in result.labels:
        plt.scatter(result.ah._x, result.ah[label], label=label)

    plt.xlabel("[M/H]")
    plt.ylabel("yield")
    arya.Legend(-1)
