import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib as mpl

from ..style.style import colors, markers, fill
from ..figure import Figure
from .data import PlotData
from .layer import Layer


class Scatter(Layer):
    marker = "o"
    size = 1
    def __init__(self, x, y, c=None, s=None, marker="o", subplot=None,
                 size=None, **kwargs):
        super().__init__(subplot)

        self.marker = marker

        if isinstance(s, (int, float)):
            size=s
            s=None

        self.size=size
        self.data = PlotData(x=x, y=y, c=c, s=s)
        self.plot()

    def plot(self, **kwargs):
        self.mpl_scat = self.mpl_ax.scatter(self.data.x, self.data.y, 
                                       marker="o", s=self.size, **kwargs)

        self.update()

    def update(self):
        self.colors = self.data.c
        self.sizes = self.data.s

    @property
    def color(self):
        if self.data.c is None:
            return self.mpl_ax.get_edgecolor()

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

        self.norm = mpl.colors.Normalize(min(cs), max(cs))
        self.cmap = mpl.cm.get_cmap()
        self.map = mpl.cm.ScalarMappable(self.norm, self.cmap)

        self._colors = self.map.to_rgba(self.data.c)

        self.mpl_scat.set_color(self._colors)

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


        self._handle = Line2D([], [], linewidth=0, marker=self.marker, 
                              markersize=self.size, facecolor=self.color, edgecolor=self.color, label = label)
