import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib as mpl
import numpy as np

from ..figure import Figure
from .data import PlotData
from .layer import Layer


class Line(Layer):
    ls = "-"
    def __init__(self, x, y, color=None, linewidth=None, subplot=None, linestyle=None, 
                 size=None, **kwargs):
        """
        A simple line plot

        Parameters
        ----------
        x: array-like
        y:
        subplot: [Defaut=None]
        color: [None]
        """

        super().__init__(subplot)
        self.set(x=x, y=y, lw=linewidth, color=color, ls=linestyle)

        self.plot(**kwargs)


    def set(self, x, y, ls, color, lw):
        self.mpl_plot = None

        self.color = color
        self.linestyle = ls
        self.linewidth = lw

        # only use subplot cycler if needed
        # so we don't increment otherwise
        if (ls is None) or (color is None):
            lcolor, lsty = self.subplot.next_linesty()
            if ls is None:
                self.linestyle = ls
            if color is None:
                self.color = lcolor

        self.data = PlotData(x=x, y=y)

        return self


    def plot(self, **kwargs):
        self.mpl_plot = self.mpl_ax.plot(self.data.x, self.data.y, lw=self.linewidth, 
                                         color=self.color, ls=self.linestyle, **kwargs)

        self.update()

    def update(self):
        pass

    # ------------- class properties --------------


    @property
    def x(self):
        return self.data.x

    @x.setter 
    def x(self, a):
        self.data.x = x
        self.mpl_plot.set_offsets(self.data.x, self.data.y)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, c):
        if self.mpl_plot is not None:
            self.mpl_plot.set_color(c)
        self._color = c


    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def linewidth(self):
        return self._lw

    @linewidth.setter
    def linewidth(self, w):
        if w is not None and self.mpl_plot is not None:
            self.mpl_plot.set_linewidth(w)
        self._lw = w

    @property
    def linestyle(self):
        if self.mpl_plot is not None:
            return self.mpl_plot.get_linestyle()
        return self._ls

    @linestyle.setter
    def linestyle(self, ls):
        if self.mpl_plot is not None:
            self.mpl_plot.set_linestyle(ls)
        self._ls = ls


    @property
    def handle(self):
        return Line2D([], [], linewidth=self.linewidth, marker=None, 
                      color=self.color, 
                      label = self.label)
