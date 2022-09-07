import matplotlib.pyplot as plt
import vice
import numpy as np
import matplotlib as mpl
import sys

sys.path.append("/home/daniel")
from python_packages.plotting import rc_params

import os

os.chdir("../..")

sys.path.append(".")
from model_comparer import ModelComparer
from plotting_utils import fig_saver

sf = fig_saver("carbon_paper/figures")

mc = ModelComparer(["cristallo11"], sf=".")

mc.plot_all_mean_stars(filename="figure3")
