from matplotlib import pyplot as plt
from .coord import Length
from .axis import Axis

class Subplot():
    def __init__(self, fig=None, size=(3,3), loc="right", row=0, col=0, axis=True):
        if fig is None:
            from .figure import Figure
            fig = Figure()

        self.fig = fig

        self.mpl_ax = self.fig.mpl_fig.add_subplot()

        self.x = Axis(self, "bottom")
        self.y = Axis(self, "left")
        self.width = size[0]
        self.height = size[1]

        self.fig.add_subplot(subplot=self, row=row, col=col)


    @property
    def fig(self):
        """ The Figure object associated with this subplot """
        return self._fig

    @fig.setter
    def fig(self, value):
        self._fig = value

    @property
    def width(self):
        """ The width of this subplot, as a Length """ 
        return self._width

    @property
    def height(self):
        return self._height

    @width.setter
    def width(self, w):
        self._width = Length(w)

    @height.setter
    def height(self, h):
        self._height = Length(h)

    @property
    def title(self):
        return self._title


    def remove(self):
        self.mpl_ax.remove()

    @property
    def h_pad(self):
        """A duple of Length representing padding to the left
        and right of the subplot
        """
        return (self.y.width, Length(0))

    @property
    def v_pad(self):
        """A duple of Length representing padding to the bottom
        and top of the subplot (respectively)
        """
        return (self.x.height, Length(0))
