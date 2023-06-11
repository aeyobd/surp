import matplotlib.pyplot as plt
import matplotlib.patheffects
import matplotlib as mpl

import sys
import os
import numpy as np


from surp.analysis.vice_model import vice_model
from surp.analysis import apogee_analysis as aah
import seaborn as sns
import arya


def main():
    filename get_args()
    model = vice_model(filename)
    directory = make_dir(filename)
    os.chdir(directory)


    os.chdir("..")


def get_args():
    if sys.argc != 2:
        print("requires 1 arg, name of model")
        raise InputError
    filename = sys.argv[1]
    
    if not os.exists(filename):
        raise InputError("file not found ", filename)
    return filename


def make_dir(filename):
    dirname, _ = os.path.splitext(os.path.basename(filename))
    if os.exists(dirname):
        raise InputError("directory already exists")
    os.makedir(dirname)
    return dirname


def plot_mdf(model):
    df = model.history
    kwargs = dict(
            histtype="step",
            density=True,
            range=(-0.3, 0.7),
            bins=100
            )
    plt.hist(df["[o/fe]"], label="model", **kwargs)
    plt.hist(aah.subgiants["MG_FE"], label="data", **kwargs)
    plt.xlabel("[Mg/Fe]")
    plt.ylabel("density")
    arya.Legend(color_only=True)
    plt.savefig("mdf.pdf")



