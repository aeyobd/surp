from matplotlib import pyplot as plt
from .coord import Length

class Axis():
    label = ""
    def __init__(self, subfig, loc="bottom"):
        self.subfig = subfig

        #mpl axis handl
        self._ax = subfig.mpl_ax
        self._fig = self._ax.figure

        if loc == "bottom":
            self.x = True
            self.mpl_axis = self._ax.get_xaxis()
        else:
            self.x = False
            self.mpl_axis = self._ax.get_yaxis()

        # init hidden vars
        self._label = ""
        self._ticks = None


    @property
    def ticks(self):
        return self._ticks

    @ticks.setter
    def ticks(self, array):
        self._ticks = array

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label
        if self.x:
            self._ax.set_xlabel(label)
        else:
            self._ax.set_ylabel(label)

    def _get_bbox(self):
        #mpl transform
        rend = self._fig.canvas.get_renderer()
        trans = self._fig.dpi_scale_trans.inverted()

        #get the bbox in inches
        return self.mpl_axis.get_tightbbox(rend).transformed(trans)


    @property
    def width(self):
        """The width of the bounding box for this axis instance"""
        return Length(self._get_bbox().width)

    @property
    def height(self):
        return Length(self._get_bbox().height)

