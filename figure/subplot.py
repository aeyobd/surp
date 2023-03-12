from matplotlib import pyplot as plt
from .coord import Length
from .axis import Axis

class Subplot():
    def __init__(self, figure=None, size=(3,3), loc="right", row=0, col=0, axis=True):
        if figure is None:
            from .figure import Figure
            figure = Figure()

        self.figure = figure

        self.mpl_ax = self.figure.mpl_fig.add_subplot()

        self.x = Axis(self, "bottom")
        self.y = Axis(self, "left")
        self.width = size[0]
        self.height = size[1]

        self.row = row
        self.col = col
        self.figure.add_subplot(subplot=self, row=row, col=col)
        self._layers = []



    @property
    def layers(self):
        return self._layers

    def add_layer(self, layer):
        self._layers.append(layer)

    @property
    def labels(self):
        return [lay.label for lay in self.layers]

    @property
    def handles(self):
        return [lay.handle for lay in self.layers]

    @property
    def figure(self):
        """ The Figure object associated with this subplot """
        return self._figure

    @figure.setter
    def figure(self, value):
        self._figure = value

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

    def locate(self, row, col):
        self.mpl_ax.set_axes_locator(self.figure.mpl_div.new_locator(nx=row, ny=col))

    def add_legend(self, legend):
        self.legend = legend
