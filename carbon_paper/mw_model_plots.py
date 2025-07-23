import matplotlib.pyplot as plt
import matplotlib
import numpy as np

import pandas as pd

import vice

import surp
from surp import subgiants
from surp import gce_math as gcem

import arya
arya.style.set_size((10/3, 10/3))
from arya import COLORS
import os

file_dir = os.path.dirname(os.path.abspath(__file__))

def find_model(name):
    """
    Finds the pickled model with either the given name or the parameters 
    and returns the csv summary
    """
    
    file_name = file_dir + "/../models/" + name + "/stars.csv"
    model =  pd.read_csv(file_name, index_col=0)
    return model


def to_nice_name(apogee_name):
    name = apogee_name.replace("_", "/").title()
    name = f"[{name}]"
    return name


data_kwargs = dict(
    color="k", 
    stat="median",
    err_kwargs=dict(facecolor="k", alpha=0.3)
)

model_kwargs = dict(
    stat="median", errorbar=None,
    aes="line"
)


def zooh_models(models, labels,x="MG_H", y="C_MG", use_true=True, sequential=False, filt_ha=True, **kwargs):
    kwargs = dict(numbins=20, **kwargs)
    
    N = len(models)
    
    if sequential:
        hm = arya.HueMap(clim=(0, N))
    else:
        hm = lambda i: COLORS[i]
    # end
        
    if use_true:
        xm=x + "_true"
        ym=y+ "_true"
    else:
        xm = x
        ym = y
    for i in range(N):
        name = labels[i]
        model = models[i]
        if filt_ha:
            df = surp.filter_high_alpha(model)
        else:
            df = model
        color = hm(i)
            
        arya.medianplot(df, xm, ym, label=name, color=color, **model_kwargs, **kwargs)
    # end

    if filt_ha:
        df = surp.filter_high_alpha(subgiants)
    else:
        df = subgiants
        
    kwargs = {"zorder":-2, **data_kwargs, **kwargs}
    arya.medianplot(df, x=x, y=y, **kwargs)
    plt.xlabel(to_nice_name(x))
    plt.ylabel(to_nice_name(y))
    

# end


    
def zofeo_models(models, labels, x="MG_FE", y="C_MG", use_true=True, sequential=False, mg_0=-0.1, w=0.05, **kwargs):
    kwargs = dict(numbins=12, x=x, y=y, **kwargs)
    df = surp.filter_metallicity(subgiants, c=mg_0, w=w)

    arya.medianplot(df, **{**data_kwargs, **kwargs})
    
    N = len(models)
    if use_true:
        kwargs["x"] = x + "_true"
        kwargs["y"] = y+ "_true"

    if sequential:
        hm = arya.HueMap(clim=(0, N))
    else:
        hm = lambda i: COLORS[i]
    # end    
    
    for i in range(N):
        model = models[i]
        df = surp.filter_metallicity(model, c=mg_0, w=w)
        color = hm(i)

        arya.medianplot(df, label=labels[i], color=color, **model_kwargs, **kwargs)
    plt.xlabel(to_nice_name(x))
    plt.ylabel(to_nice_name(y))
    

def names_to_models(names):
    return [find_model(name) for name in names]

def compare_cooh(names, labels, ylim=None, legend=True, **kwargs):
    models = names_to_models(names)
    zooh_models(models, labels,legend=legend, **kwargs)
    if legend:
        arya.Legend(color_only=True)
    
    if ylim is not None:
        plt.ylim(ylim)
    else:
        plt.ylim(-0.4, 0.04)
        #plt.yticks(np.arange(-0.2, 0.02, 0.05))
    # end if
    
    plt.xlim(-0.45, 0.35)


def compare_coofe(names, labels, legend=True, ylim=None, **kwargs):
    models = names_to_models(names)
    zofeo_models(models, labels, legend=legend, **kwargs)
    if legend:
        arya.Legend(color_only=True)

    plt.xlim(-0.00, 0.4)


def compare(names, labels=None, axs=None, **kwargs):
    if labels is None:
        labels = names
        
    if axs is None:
        fig, axs = plt.subplots(1, 2, figsize=(7, 3), sharex="col", sharey=True,  gridspec_kw={"wspace": 0, "hspace": 0})
    # end
        
    plt.sca(axs[0])
    compare_cooh(names, labels, **kwargs, legend=False)
    
    plt.sca(axs[1])
    compare_coofe(names, labels, legend=False, **kwargs)
    plt.ylabel("")
    arya.Legend(color_only=True)


