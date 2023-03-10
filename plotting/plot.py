import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from functools import singledispatchmethod

from ..figure import Subfig
from . import PlotData
from . import Scatter

class Plot():
    def __init__(self, x, y, axes=None, **kwargs):
        self.x = x
        self.y = y

        self.axes = axes

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, s):
        if s == "scatter":
            self._kind = Scatter(self)

    def plot(self):
        self.kind.plot()

    @property
    def axes(self):
        return self._axes

    @axes.setter
    def axes(self, ax):
        if ax is None:
            self.ax = Axes(self)
        else:
            ax.attach(self)
            self.ax = ax
