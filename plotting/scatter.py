import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib as mpl

from ..style.style import colors, markers, fill
from ..figure import Figure
from .data import PlotData
from .layer import Layer


class Scatter(Layer):
    def __init__(self, x, y, c=None, s=None, m=None, marker=None, subplot=None,
                 size=None, cats=None, **kwargs):
        super().__init__(subplot)
        self.marker = marker

        if isinstance(s, (int, float)):
            size=s
            s=None
            print(size)

        self.cats = cats
        self.size=size
        self.data = PlotData(x=x, y=y, c=c, s=s, m=m)
        self.plot()

    def plot(self, **kwargs):
        if self.cats is not None and len(self.cats):
            self.plot_cats(**kwargs)

        if any([cat in ("c", "s", "m") for cat in self.data.cats]):
            self.cats = self.data.cats
            self.plot_cats(**kwargs)


        self.mpl_scat = self.mpl_ax.scatter(self.data.x, self.data.y, 
                                       marker="o", **kwargs)

        self.update()

    def update(self):
        self.colors = self.data.c
        self.sizes = self.data.s

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
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, labels):
        self._labels = labels

        self._handles = []
        for label in labels:
            self._handles.append(Line2D([], [], linewidth=0, marker="o",
                                 label = label)
                                 )
