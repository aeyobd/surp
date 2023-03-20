import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib as mpl
import pandas as pd

from ..style.style import colors, markers, fill
from ..figure import Figure
from .data import PlotData
from .layer import Layer
from .scatter import Scatter


class Scatters():
"""
A class for creating scatter plots with multiple labels

e.g. 
scatter over c or s or m.

Note this is technically a container over multiple layers 
and only works with pandas dataframes

"""
    def __init__(self, df, x, y, c=None, s=None, m=None, 
                 marker=None, subplot=None, size=None, 
                 labels=None, **kwargs):

        super().__init__(subplot)

        self.marker = marker
        self.labels = labels
        self.size = size

        self.c = c
        self.s = s
        self.m = m

        self.data = PlotData(df=df, x=x, y=y, c=c, s=s, m=m)
        self.plot()

    def get_cats(self):
        self.cats = []
        if type(s) is str:
            self.cats.append["s"]
        if type(c) is str:
            self.cats.append["c"]
        if type(m) is str:
            self.cats.append["m"]

        if "c" in self.cats and "m" in self.cats:
            self.cm = self.c == self.m

    def set_labels(self):
        if (len(self.cats) - self.cm) == 1:
            self.labels = pd.unique(self.data[self.cats[0]])
        else:
            print("NotImplemented")


    def plot_cat(self, **kwargs):
        pass

