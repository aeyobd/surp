import matplotlib.pyplot as plt
import mpl_toolkits.axes_grid1 as maxie

from .subplot import Subplot
from .figure import Figure
from .coord import Length
from ..style.style import FIG_SIZE


class JoinPlot(Subplot):
    def __init__(self, nrows=1, ncols=1, row=1, col=1, size=None, figure=None, hpad=0, vpad=0):
        if figure is None:
            figure = Figure(dpi=1000)

        if size is None:
            size = (FIG_SIZE[0]*ncols, FIG_SIZE[1]*nrows)

        self.width = size[0]
        self.height = size[1]

        self.figure = figure
        self.mpl_axs = maxie.axes_grid.Grid(figure.mpl_fig, 111, (nrows, ncols), 
                                            axes_pad=(hpad, vpad))

        self.nrows = nrows
        self.ncols = ncols
        self.make_children()
        self.figure.add_subplot(self, row=row, col=col)

    def locate(self, row, col):
        self.mpl_axs.set_axes_locator(self.figure.mpl_div.new_locator(nx=row, ny=col))

    def make_children(self):
        self.children = [[None]*self.ncols for _ in range(self.nrows)]

        for i in range(self.nrows):
            for j in range(self.ncols):
                child = Subplot(self.figure, add_to_fig=False,
                                ax=self.mpl_axs[self.ncols*i + j])
                self.children[i][j] = child
                # child.mpl_ax.set_xticks(child.mpl_ax.get_xticks()[1:-1])


    @property
    def xlabel(self):
        return self._xlabel

    @xlabel.setter
    def xlabel(self, l):
        self._xlabel = l

    @property
    def xlim(self):
        pass

    @property
    def h_pad(self):
        ax_w = max([child.h_pad[0] for child in [row[0] for row in self.children]])

        return (ax_w, Length(0))

    @property
    def v_pad(self):
        ax_h = max([child.v_pad[0] for child in self.children[-1]])

        return (ax_h, Length(0))


def forceAspect(ax,aspect=1):
    #aspect is width/height
    scale_str = ax.get_yaxis().get_scale()
    xmin,xmax = ax.get_xlim()
    ymin,ymax = ax.get_ylim()
    if scale_str=='linear':
        asp = abs((xmax-xmin)/(ymax-ymin))/aspect
    elif scale_str=='log':
        asp = abs((scipy.log(xmax)-scipy.log(xmin))/(scipy.log(ymax)-scipy.log(ymin)))/aspect
    ax.set_aspect(asp)
