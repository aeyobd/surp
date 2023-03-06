from .figbase import FigBase
from .subplot import Subplot
from .coord import Length


class SubFigure(FigBase):
    children = [[]]

    def __init__(self, fig, n_rows=1, n_cols=1, make_subplots=True, **kwargs):

        self.n_rows = n_rows
        self.n_cols = n_cols
        self.fig = fig

        if make_subplots:
            self.make_subplots()
        else:
            pass

    def make_subplots(self)
        subplots = [ [None]*self.n_rows for _ in self.n_cols ]
        for i in range(rows):
            for j in range(cols):
                self.children[i][j] = add_subfig(row=i, col=j)

