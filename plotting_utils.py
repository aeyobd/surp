import matplotlib.pyplot as plt
import numpy as np
from functools import wraps
import rc_params

class fig_saver():
    def __init__(self, output_dir = ".", show=True):
        self.show = show
        if output_dir[-1] == "/":
            self.output_dir = output_dir
        else:
            self.output_dir = output_dir + "/"

    def save(self, name, fig=None):
        if fig is None:
            fig = plt.gcf()
        fig.savefig(self.output_dir + name + ".pdf", facecolor="white", bbox_inches='tight', dpi=150)
        fig.savefig(self.output_dir + name + ".jpeg", facecolor="white", bbox_inches='tight', dpi=150)
        if self.show:
            plt.show()

    def __call__(self, name, fig=None):
        self.save(name, fig=fig)



def legend_outside(**kwargs):
    plt.legend(bbox_to_anchor=(1,1), loc="upper left", **kwargs)

def fancy_legend(ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()
       
    prop_cycle = plt.rcParams['axes.prop_cycle']
    COLORS = prop_cycle.by_key()['color']
    leg = ax.legend(frameon = False, handlelength = 0, columnspacing = 0.8, 
                     fontsize = 20, **kwargs)
    for i in range(len(leg.get_texts())):
        leg.get_texts()[i].set_color(COLORS[i])
        leg.legendHandles[i].set_visible(False)


def arg(name, arg_type=object, value_constraint=True, default_value="None"):
    """A wrapper funcion to check arguments"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if type(name) == str:
                if name in kwargs.keys():
                    x = kwargs[name]
                else:
                    x = exec(default_value)
                print(kwargs)
                print(globals())
                print(locals())
                x = exec(name)

            elif type(name) == int:
                if name < len(args) and name >= 0:
                    x = args[name]
                else:
                    raise ValueError("If name is an integer, it must be between 0 and len(args)-1")

            else:
                raise TypeError("Type of name must be an integer or string. Got %s instead" % str(type(name)))


            if not isinstance(x, arg_type):
                raise TypeError("Argument %s must be of type %s. Got %s instead" %(name, arg_type, type(x)))
            if not value_constraint:
                raise ValueError("Argument %s must satisfy %s" %(name, value_constraint))

            return func(*args, **kwargs)

        return wrapper
    return decorator



# @arg("ylim", default_value="(min(y), max(y))")
# @arg("xlim", default_value="(min(x), max(x))")
def density_scatter(x, y, xlim=None, ylim=None, n_bins=100, fig=None, ax=None, dropna=True, density=True, **kwargs):
    """
    Plots the density of the data in each bin provided there is data in the bin. 
    The function wrapps matplotlib.pyplot.hist2d, calculating the bins for the histogram.

    Parameters
    ----------
    x: listlike
        The x values of each data point to plot
    y: listlike
        The y values of each data point to plot
    xlim: (float, float)
        The lower and upper bounds on the x axis
    ylim: (float, float)
        The lower and upper bounds of the y axis
    n_bins: int
        The number of bins to divide each axis into
    dropna: bool
    
    Returns
    -------
    The four outputs from hist2d
    """
    if xlim is None:
        xlim = (min(x), max(x))
    if ylim is None:
        ylim = (min(y), max(y))

    if fig is None or ax is None:
        fig, ax = plt.subplots()

    x_bins = np.linspace(xlim[0], xlim[1], n_bins)
    y_bins = np.linspace(ylim[0], ylim[1], n_bins)

    if dropna:
        filt = np.isnan(x) | np.isnan(y)


    R =  ax.hist2d(x[~filt], y[~filt], bins=[x_bins, y_bins], cmin=1, density=density, **kwargs)

    _, _, _, f = R

    if density:
        fig.colorbar(f, label="Density", ax=ax)
    else:
        fig.colorbar(f, label="Count", ax=ax)
       
    return R

