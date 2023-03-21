### Abstract class for plots

from .. import Figure


class Layer:
    def __init__(self, subplot=None):
        if subplot is None:
            fig = Figure(add_subplot=True)
            subplot = fig.children[0][0]

        self.subplot = subplot
        self.subplot.add_layer(self)

        self.mpl_ax = self.subplot.mpl_ax
        self.label = ""

    def update(self):
        pass

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, l):
        self._label = l


    @property
    def handle(self):
        return self._handle

    @handle.setter
    def handle(self, h):
        self._handle = h

