from matplotlib import pyplot as plt

class Legend:
    def __init__(self, subplot):
        self.labels = subplot.labels

        self.mpl_leg = subplot.mpl_ax.legend(subplot.handles, self.labels, frameon=False)
        subplot.add_legend(self)

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, a):
        self._labels = a

    @property
    def handles(self):
        return self.mpl_leg.legendHandles

    @property
    def ms(self):
        return [h.get_markersize() for h in self.handles]

    @ms.setter
    def ms(self, size):
        if isinstance(size, (int, float)):
            for h in self.mpl_leg.legendHandles:
                h.set_markersize(size)
        elif isinstance(size, (tuple, list)):
            if len(size) != len(self.handles):
                raise ValueError("size must be same len as handles")
            for h in self.handles:
                h.set_markersize(size)

    @property
    def show_handles(self):
        return self._show_handles

    @show_handles.setter
    def show_handles(self, boo):
        for h in self.handles:
            h.set_visible(boo)
        self._show_handles = boo

        if boo:
            self.mpl_leg.handlelength = 2.0
            self.mpl_leg.columnspacing = 2.0
        else:
            self.mpl_leg.handlelength = 0
            self.mpl_leg.columnspacing = 0

    @property
    def color_labels(self):
        return self._color_labels

    @color_labels.setter
    def color_labels(self, boo):
        texts = self.mpl_leg.get_texts()
        if boo:
            for t, c in zip(texts, self.colors):
                t.set_color(c)
        else:
            for t in texts:
                t.set_color("k")
        self._color_labels = boo

    @property
    def colors(self):
        return [h.get_color() for h in self.handles]





