import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib as mpl
import numpy as np

from ..figure import Figure
from .data import PlotData
from .layer import Layer
from ..style.style import get_cmap


class Scatter(Layer):
    marker = "o"
    size = 1
    def __init__(self, x, y, c=None, s=None, marker="o", subplot=None, size=None, **kwargs):
        """
        A simple scatter plot

        Parameters
        ----------
        x: array-like
        y:
        c:
        s:
        marker:
        subplot: [Defaut=None]
        size: [None]
        """

        super().__init__(subplot)
        self.set(x=x, y=y, c=c, s=s, size=size, marker=marker)
        self.plot(**kwargs)


    def set(self, x, y, c, s, size, marker):
        self.mpl_scat = None
        self._color = None

        if isinstance(s, (int, float)):
            size=s
            s=None

        self.marker = marker

        # only use subplot cycler if needed
        # so we don't increment otherwise
        if (marker is None) or (c is None):
            mcolor, msty = self.subplot.next_marksty()
            if marker is None:
                self.marker = msty
            if c is None:
                self.color = mcolor

        self.data = PlotData(x=x, y=y, c=c, s=s)
        self.size=size

        if c is not None:
            self.clim = (min(c), max(c))

        return self


    def plot(self, **kwargs):
        self.mpl_scat = self.mpl_ax.scatter(self.data.x, self.data.y, 
                                       marker="o", s=self.size, **kwargs)

        self.update()

    def update(self):
        self.colors = self.data.c
        self.sizes = self.data.s

    def map(self, x:float) -> tuple:
        if self.data.c is None:
            return None

        return self.mpl_map.to_rgba(x)


    # ------------- class properties --------------

    @property 
    def clim(self):
        return self._clim

    @clim.setter
    def clim(self, clh: tuple):
        self._clim = clh

        norm = mpl.colors.Normalize(*self.clim)
        cmap = get_cmap()
        self.mpl_map = mpl.cm.ScalarMappable(norm, cmap)

        self.update()


    @property
    def x(self):
        return self.data.x

    @x.setter 
    def x(self, a):
        self.data.x = x
        self.mpl_scat.set_offsets(self.data.x, self.data.y)

    @property
    def colors(self):
        return self._colors

    @colors.setter
    def colors(self, cs):
        if cs is None:
            self._colors = None
            return 

        self.data.c = cs
        if self.mpl_scat is not None:
            self.mpl_scat.set_color(self.map(self.data.c))

    @property
    def color(self):
        if self.data.c is None:
            return self.mpl_scat.get_edgecolor()[0]
        else:
            return (0.0, 0.0, 0.0, 1.0)

    @color.setter
    def color(self, c):
        if self.mpl_scat is not None:
            self.mpl_scat.set_color(c)
        self._color = c


    @property
    def sizes(self):
        return self._sizes

    @sizes.setter
    def sizes(self, ss):
        if ss is not None:
            self.mpl_scat.set_sizes(ss)
        self._sizes = ss


    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label


    @property
    def handle(self):
        return Line2D([], [], linewidth=0, marker=self.marker, 
                      markersize=self.size, color=self.color, 
                      label = self.label)
