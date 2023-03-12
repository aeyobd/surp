from ..figure.subplot import Subplot
from ..figure.coord import Length
import matplotlib.pyplot as plt
from ..figure.axis import Axis

class Colorbar(Subplot):
    cmin = 0
    cmax = 1
    def __init__(self, layer):

        self.layer = layer
        self._sp = layer.subplot
        self.figure = self._sp.figure

        row = self._sp.row
        col = self._sp.col + 1 # create to the right of the subfigure


        self._width = self._sp.width * 0.05
        self._height = self._sp.height

        self.map = self.layer.map

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
        return self._labels

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
