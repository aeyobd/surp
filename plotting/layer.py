### Abstract class for plots

from .. import Figure


class Layer:
    def __init__(self, subplot=None):
        if subplot is None:
            fig = Figure()
            subplot = fig.children[0][0]

        self.subplot = subplot
        self.mpl_ax = self.subplot.mpl_ax

    def update(self):
        pass

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, l):
        self._labels = l


    @property
    def handles(self):
        return self._handles

    @handles.setter
    def handles(self, h):
        self._handles = h

