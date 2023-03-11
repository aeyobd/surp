
from matplotlib import pyplot as plt

class Legend:
    def __init__(self, layer):
        # self.markers, self.labels = layer.mpl_ax.get_legend_handles_labels()
        self.labels = layer.labels
        self.handles = layer.handles

        self.mpl_leg = layer.mpl_ax.legend(self.handles, self.labels)

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, a):
        self._labels = a

    @property
    def handles(self):
        return self._handles

    @handles.setter
    def handles(self, l):
        self._handles = l
