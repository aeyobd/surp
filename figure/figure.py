from functools import singledispatch
from os import path

import matplotlib as mpl
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import Divider, Size

from .coord import Length, Coordinate
from .subplot import Subplot
from .figbase import FigBase
plt.rcParams['figure.constrained_layout.use'] = False

padding = 0.2



class Figure(FigBase):

    def __init__(self, size=(), **kwargs):
        self.mpl_fig = plt.figure()
        self._fig = self.mpl_fig
        self.children = [[]]
        self.floats = [] # TODO: for legends/etc.

        self.h_pad = (Length(0.0), Length(0.0))
        self.v_pad = (Length(0.0), Length(0.0))

        self.add_subplot()
        self.update()

    def add_subplot(self, subplot=None, loc=None, row=0, col=0):
        # to add children if not there
        self._fill_array(row, col)
        self.remove_child(row, col)

        if subplot is None:
            subplot = Subplot(self, row=row, col=col)
            self.children[row][col] = subplot
        else:
            self.children[row][col] = subplot
            self.update()

        return subplot

    def remove_child(self, row=0, col=0):
        if self.n_rows > 0 and self.n_cols > 0:
            self.children[row][col].remove()
            del self.children[row][col]
            self.children[row].insert(col, FigBase())

    def add_subfig(self):
        pass # this is for nested array elements ...

    def _fill_array(self, row: int, col: int):
        for i in range(row + 1):
            if self.n_rows < i+1:
                self.children.append([])

            for j in range(col + 1):
                if len(self.children[i]) < j + 1:
                    self.children[i].append(FigBase())

    def set_div(self):
        index = 1
        horizontal = [l.mpl for l in self.h_divs]
        vertical = [l.mpl for l in self.v_divs]
        self.mpl_div = Divider(self.mpl_fig, (0,0,1,1), 
                               horizontal=horizontal, vertical=vertical)

        for i in range(self.n_rows):
            for j in range(self.n_cols):
                child = self.children[i][j]
                nx = 2*j + 1
                ny = 2*i + 1
                child.mpl_ax.set_axes_locator(self.mpl_div.new_locator(nx=nx, ny=ny))

    @property
    def h_divs(self):
        h_divs = []
        pad_sep = Length(padding)
        pad_sep += self.h_pad[0]

        for i in range(self.n_cols):
            child = self.children[0][i]
            pad_sep += child.h_pad[0]
            h_divs.append(pad_sep)

            h_divs.append(child.width)

            pad_sep = Length(padding)
            pad_sep += child.h_pad[1]

        pad_sep += self.h_pad[1]
        h_divs.append(pad_sep)
        return h_divs

    @property
    def v_divs(self):
        v_divs = []
        pad_sep = Length(padding)
        pad_sep += self.v_pad[1]

        for i in range(self.n_rows):
            child = self.children[i][0]
            pad_sep += child.v_pad[0]
            v_divs.append(pad_sep)

            v_divs.append(child.height)

            pad_sep = Length(padding)
            pad_sep += child.v_pad[1]

        pad_sep += self.v_pad[1]
        v_divs.append(pad_sep)
        return v_divs


    def update(self):
        self.set_div()

        self._fig.set_figwidth(self.width.inch)
        self._fig.set_figheight(self.height.inch)
        self._fig.canvas.draw_idle()


    def show(self):
        self.update()
        plt.show()

    def save(self, filename):
        self.update
        self._fig.savefig(self.output_dir + name + ".pdf", facecolor="white", 
                         dpi=150)

        if self.show:
            plt.show()

    @property
    def width(self):
        w = Length(0)
        for l in self.h_divs:
            w += l
        return w

    @property
    def height(self):
        h = Length(0)
        for l in self.v_divs:
            h += l
        return h

    @property
    def sp(self):
        if len(self.children) == 1 and len(self.children[0]) == 1:
            return self.children[0][0]
