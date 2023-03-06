from matplotlib import pyplot as plt


prop_cycle = plt.rcParams["axes.prop_cycle"]
COLORS = prop_cycle.by_key()['color']

class Legend():
    def __init__(self, **kwargs):
        self.mpl_legend = plt.legend(**kwargs)

    def fancy(self, **kwargs):
        del self.mpl_legend

        self.mpl_legend = self.mpl_ax.legend(frameon=False, handlelength=0, 
                                             columnspacing=0.8, **kwargs)
        for i in range(len(self.mpl_legend.get_texts())):
            self.mpl_legend.get_texts()[i].set_color(COLORS[i % len(COLORS)])
            self.mpl_legend.legendHandles[i].set_visible(False)
