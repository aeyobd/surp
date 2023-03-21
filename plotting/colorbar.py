from ..figure.subplot import Subplot
from ..figure.coord import Length
import matplotlib.pyplot as plt
from ..figure.axis import Axis

class Colorbar(Subplot):
    cmin = 0
    cmax = 1
    def __init__(self, layer=None, subplot=None, mappable=None, figure=None, 
                 row=None, col=None, width=None):

        self.layer = layer

        if subplot is None:
            subplot = layer.subplot
        self._sp = subplot

        if figure is None:
            figure = self._sp.figure
        if row is None:
            row = self._sp.row
        if col is None:
            col = self._sp.col + 1 # create to the right of the subfigure

        self.figure = figure

        if width is None:
            self._width = self._sp.width * 0.05
        else:
            self._width = width

        self._height = self._sp.height

        if mappable is None:
            mappable = self.layer.mpl_map
        self.map = mappable

        self.mpl_ax = self.figure.mpl_fig.add_subplot()

        self.mpl_cb = plt.colorbar(mappable=self.map, cax=self.mpl_ax)
        self.ax = Axis(self, loc="right")

        self.figure.add_subplot(subplot=self, row=row, col=col)

    @property
    def cmin(self):
        return self._cmin

    @cmin.setter
    def min(self, m):
        self._cmin = m
        self.ax.lim = (self.cmin, self.cmax)

    @property
    def cmax(self):
        return self._cmin

    @min.setter
    def cmax(self, m):
        self._min = m
        self.ax.lim = (self.cmin, self.cmax)

    @property
    def label(self):
        return self.ax.label

    @label.setter
    def label(self, l):
        self.ax.label = l

    @property
    def markers(self):
        return self._markers

    @property
    def axis(self):
        return self._axis

    @property
    def norm(self):
        return self._norm

    @property
    def cmap(self):
        return self._cmap

    @property
    def h_pad(self):
        return (self.width, self.ax.width)

    @property
    def v_pad(self):
        return (Length(0), Length(0))
