import matplotlib.pyplot as plt
import numpy as np
from functools import wraps
from . import rc_params
from matplotlib.collections import LineCollection
import scipy

prop_cycle = plt.rcParams['axes.prop_cycle']
COLORS = prop_cycle.by_key()['color']

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

def fancy_legend(ax=None, colors=COLORS, **kwargs):
    if ax is None:
        ax = plt.gca()
       
    leg = ax.legend(frameon = False, handlelength = 0, columnspacing = 0.8, 
                     fontsize = 20, **kwargs)
    for i in range(len(leg.get_texts())):
        leg.get_texts()[i].set_color(colors[i % len(colors)])
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

def plot_thick_line(x, y, w, i=0, xlim=None, ylim=None, ax=None, **kwargs):
    w_max = np.nanmax(w)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    if ax is None:
        ax = plt.gca()

    lwidths = w/w_max * 5
    lc = LineCollection(segments, linewidths=lwidths, color=COLORS[i], **kwargs)
    ax.add_collection(lc)

    if xlim is None:
        ax.set_xlim(np.nanmin(x), np.nanmax(x))
    if ylim is None:
        ax.set_ylim(np.nanmin(y), np.nanmax(y))

def plot_density_line(x, y, **kwargs):
    """
    This method is like plt.plot except plots
    the line with a variable width which represents how 
    clustered the data are

    Parameters
    ----------
    x: list like
    y: list like
    **kwargs:
        Passed to plt.plot

    """
    lw_max = 10
    lw_min = 1

    ds_min = 1e-9

    dx = differential(x)
    dy = differential(y)
    ds = np.sqrt(dx**2 + dy**2) 
    w = 1/ds 
    w_scaled = (w - np.nanmin(w))/(np.nanmax(w) - np.nanmin(w))
    lwidths = (-lw_min + lw_max)*w_scaled + lw_min

    plot_thick_line(x, y, lwidths, **kwargs)

def dual_plot():
    fig = plt.figure(figsize=(10, 5))
    gs = fig.add_gridspec(1, 2, wspace=0)
    axs = gs.subplots(sharey=True)

    return fig, axs

def differential(l):
    """
    Calculates the differentail of a list l.

    Parameters
    ----------
    l:  list like
        A list of which to calculate the differential

    Returns
    -------
    dl:     ``np.list``
        A list of the change between each value of l
    """

    li = np.array(l)[:-1]
    lf = np.array(l)[1:]
    dl = li-lf

    d_end = dl[-1]
    return np.append(dl, d_end)

def plot_mean_track(x_vals, y_vals, bins=30, xlim=None, shade_width=False, err_mean = False, ax=None, dropna=False, **kwargs):
    """
    Plots the mean of the data as a line
    with a shaded region representing the standard deviation
    
    Parameters
    ----------
    
    x_vals: np.array like
        The x values of the data
        
    y_vals: np.array like
    bins: ``int`` [default: 50]
        The number of bins to bin the data by
    xlim: ``(int, int)`` [default: None]
        The limits of the bins of the data
        if None, uses the minimum and maximum values
    err_mean: ``bool`` [default: False]
        If true, plots the error of the mean instead
        of the standard deviation for the shaded regions
    """

    if ax is None:
        ax = plt.gca()
        
    if dropna:
        filt = ~(np.isnan(x_vals) | np.isnan(y_vals))
        x_vals = x_vals[filt]
        y_vals = y_vals[filt]
    means, bins, _ = scipy.stats.binned_statistic(x_vals, y_vals, statistic="mean", bins=bins, range=xlim)
    nums, _, _ = scipy.stats.binned_statistic(x_vals, y_vals, statistic="count", bins=bins, range=xlim)
    x_bins = 0.5*(bins[1:] + bins[:-1])
    p = ax.plot(x_bins, means, **kwargs)
    # p = plot_thick_line(x_bins, means, nums/30, ax=ax, **kwargs)
    

    if shade_width:
        std, _, _ = scipy.stats.binned_statistic(x_vals, y_vals, statistic="std", bins=bins, range=xlim)
        if err_mean:
            dy = std / np.sqrt(nums)
        else:
            dy = std
        ax.fill_between(x_bins, means - dy, means + dy, alpha=0.3, color=p[0].get_color())



    return means, bins, nums