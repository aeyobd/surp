import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patheffects
import numpy as np
import pandas as pd
import vice
import seaborn as sns
import warnings

import surp
from surp import gce_math as gcem
from surp.yields import calc_y
import arya

TMAX = 13.2
CLIM = (-TMAX, 0)
CMAP = "arya_r"

def colored_line(x, y, c, ax, **lc_kwargs):
    """
    Plot a line with a color specified between (x, y) points by a third value.

    It does this by creating a collection of line segments between each pair of
    neighboring points. The color of each segment is determined by the
    made up of two straight lines each connecting the current (x, y) point to the
    midpoints of the lines connecting the current point with its two neighbors.
    This creates a smooth line with no gaps between the line segments.

    Parameters
    ----------
    x, y : array-like
        The horizontal and vertical coordinates of the data points.
    c : array-like
        The color values, which should have a size one less than that of x and y.
    ax : Axes
        Axis object on which to plot the colored line.
    **lc_kwargs
        Any additional arguments to pass to matplotlib.collections.LineCollection
        constructor. This should not include the array keyword argument because
        that is set to the color argument. If provided, it will be overridden.

    Returns
    -------
    matplotlib.collections.LineCollection
        The generated line collection representing the colored line.
    """
    if "array" in lc_kwargs:
        warnings.warn('The provided "array" keyword argument will be overridden')

    # Check color array size (LineCollection still works, but values are unused)
    if len(c) != len(x) - 1:
        warnings.warn(
            "The c argument should have a length one less than the length of x and y. "
            "If it has the same length, use the colored_line function instead."
        )

    # Create a set of line segments so that we can color them individually
    # This creates the points as an N x 1 x 2 array so that we can stack points
    # together easily to get the segments. The segments array for line collection
    # needs to be (numlines) x (points per line) x 2 (for x and y)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = mpl.collections.LineCollection(segments, **lc_kwargs)

    # Set the values used for colormapping
    lc.set_array(c)

    return ax.add_collection(lc)



def plot_tracks(h, ax = plt.gca(), Rs = np.arange(2, 15), x="MG_H", y="C_MG", c="time"):
    for R in Rs:
        df = h[np.isclose(h.R, R - 0.05)][1:]
        xs = df[x]
        ys = df[y]
        cs = df[c].values
        cs = (cs[1:]+ cs[:-1])/2
        cs = cs - TMAX

        lines = colored_line(xs, ys, cs, ax, rasterized=True, clim=CLIM, cmap=CMAP)



def plot_labels(h, Rs = [4, 8, 12], offsets = None, labels = None, x="MG_H", y="C_MG"):

    if offsets is None:
        offsets = [(0., 0.) for _ in range(len(Rs))]

    elif isinstance(offsets, tuple):
        offsets = [offsets for _ in range(len(Rs))]

    if labels is None:
        labels = []
        for R in Rs:
            labels.append(str(R))

    for i, R in enumerate(Rs):
        df = h[np.isclose(h.R, R - 0.05)]
        xs = df[x].iloc[-1] 
        ys = df[y].iloc[-1]

        offset = offsets[i]

        text = plt.annotate(labels[i], xy=(xs, ys),  
            zorder=20, ha="center", va="bottom",  xycoords='data', 
            textcoords='offset points', xytext=offset)





def make_plot(h):
    h = fiducial.history
    fig, axs = plt.subplots(1, 2, sharey=True, gridspec_kw={"wspace": 0}, figsize=(7, 10/3), dpi=350)

    plt.sca(axs[0])

    plot_tracks(h, ax=axs[0])
    plot_labels(h, Rs=[4,8,12], labels=["4 kpc", "8", "12"])

    plt.xlim(-2.5, 0.7)
    plt.xlabel("[Mg/H]")
    plt.ylabel("[C/Mg]")


    # RHS

    plt.sca(axs[1])

    plot_tracks(h, x="MG_FE", y="C_MG", ax=axs[1])
    plot_labels(h, x="MG_FE", y="C_MG", offsets=[(0,0), (0,0), (6,0)])

    plt.xlim(-0.06, 0.48)
    plt.ylim(-0.55, 0.05)
    plt.xlabel("[Mg/Fe]")

    # colorbar
    cax = axs[1].inset_axes([1.05, 0., 0.05, 1])
    cb = arya.Colorbar(clim=CLIM, label=r"lookback time (Gyr)", cmap=CMAP, cax=cax)



if __name__ == "__main__":

    model_dir = "../../models/fiducial/run"

    fiducial = surp.ViceModel.from_file(model_dir + "/model.json")

    yp = surp.yields.YieldParams.from_file(model_dir + "/yield_params.toml")
    surp.yields.set_yields(yp)

    h = fiducial.history

    make_plot(h)
    plt.savefig("figures/all_the_tracks.pdf")

