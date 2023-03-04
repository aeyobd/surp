import matplotlib as mpl

import pyplot as plt

class figure:
    """
    This class is designed to 
    make modifications and handeling MPL's
    figure class easier
    """
    __init__(**kwargs):
        self.create_fig()

    create_fig(self, **kwargs):
        self.fig, self.ax = mpl.figure(**kwargs)

    resize_fig(self):
        ax_width


    @property
    def ax_width(self):
        return (self.fig.subplotpars.right -
                self.fig.subplotpars.left)*self.fig.get_figwidth()

    @property
    def ax_heighth(self):
        return (self.fig.subplotpars.top -
                self.fig.subplotpars.bottom)*self.fig.get_figheighth()

