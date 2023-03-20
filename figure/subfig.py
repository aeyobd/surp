from .figbase import FigBase
from .subplot import Subplot
from .coord import Length
from .figure import Figure

import matplotlib.pyplot as plt

class SubFigure(Figure):
    children = [[]]

    def __init__(self, nrows=1, ncols=1, **kwargs):
        self.nrows = nrows
        self.ncols = ncols
        self.mpl_fig = plt.figure()
        self.mpl_sfs = self.mpl_fig.subfigures(nrows, ncols, **kwargs)

        self.children = [[None]*ncols for _ in range(nrows)]

        if nrows > 1:
            for i in range(nrows):
                if ncols > 1:
                    for j in range(ncols):
                        self.children[i][j] = Figure(mpl_fig = self.mpl_sfs[i][j])
                else:
                    self.children[i][0] = Figure(mpl_fig=self.mpl_sfs[i])
        else:
            if ncols > 1:
                for j in range(ncols):
                    self.children[0][j] = Figure(mpl_fig = self.mpl_sfs[j])
            else:
                self.children[0][0] = Figure(mpl_fig = self.mpl_sfs)

        self.h_pad = (Length(0.0), Length(0.0))
        self.v_pad = (Length(0.0), Length(0.0))

