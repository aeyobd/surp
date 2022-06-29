import numpy as np
import random
import matplotlib.pyplot as plt
import vice
import seaborn as sns

AGB_MODELS = ["cristallo11", "karakas10", "ventura13", "karakas16"]


def analogdata(filename):
    # from VICE/src/utils
    # last column of analogdata is z_height_final
    data = []
    with open(filename, 'r') as f:
        line = f.readline()
        while line[0] == '#':
            line = f.readline()
        while line != '':
            line = line.split()
            data.append([int(line[0]), float(line[1]), float(line[-1])])
            line = f.readline()
        f.close()
    return data

def calculate_z(output):
    analog_data = analogdata(output.name + "_analogdata.out")
    return [np.abs(row[-1]) for row in analog_data][:output.stars.size[0]]


def sample_stars(stars, num=1000):
    r"""
    Samples a population of stars while respecting mass weights

    Parameters
    ----------
    stars: the stars attribute from vice.output
    num: (int) the number of stars to sample

    Returns
    -------
    A np.array of the sampled parameter from stars
    """
    size = len(stars.todict()["mass"])
    result = {key: np.zeros(num) for key in stars.keys()}

    index = random.choices(np.arange(size), weights=stars["mass"], k=num)
    for i in range(num):
        for key in stars.keys():
            result[key][i] = stars[key][index[i]]
    return vice.dataframe(result)

def filter_stars(stars, R_min, R_max, z_min=0, z_max=2):
    return stars.filter("zone_final", ">", R_to_zone(R_min)).filter(
        "zone_final", "<", R_to_zone(R_max)).filter(
        "abs_z", ">", z_min).filter(
        "abs_z", "<", z_max)

def show_at_R_z(stars, x="[fe/h]", y=None, c=None, xlim=None, ylim=None, **kwargs):
    r"""Creates a grid of plots at different R and z of show_stars

    Parameters
    ----------

    

    """
    fig, axs = plt.subplots(5, 3, sharex=True, sharey=True, figsize=(15,15), squeeze=True)
    # fig.supxlabel(x)
    # fig.supylabel(y)

    vmin = None
    vmax = None
    if c is not None:
        vmin = min(stars[c])
        vmax = max(stars[c])

    for j in range(5):
        R_min, R_max = [(3,5), (5,7), (7,9), (9,11), (11,13)][j]

        for i in range(3):
            z_min, z_max = [(0, 0.5), (0.5, 1), (1, 1.5)][i]
            filtered = sample_stars(filter_stars(stars, R_min, R_max, z_min, z_max), num=1000)

            ax = axs[j][i]
            im = show_stars(filtered, x, y, c=c, colorbar=False, fig=fig, ax=ax, vmin=vmin, vmax=vmax, **kwargs)
            ax.set(xlim=xlim,
                   ylim=ylim,
                   xlabel="",
                   ylabel=""
                  )
            if i == 0:
                ax.set(ylabel="R = %i - %i kpc" %(R_min, R_max))
            if j == 4:
                ax.set(xlabel="|z| = %1.1f - %1.1f" % (z_min, z_max))

    if c is not None:
        fig.colorbar(im, ax=axs.ravel().tolist(), label=c)



def show_stars(stars, x="[fe/h]", y=None, c=None, s=1, alpha=1, kde=False, ax=None, fig=None, colorbar=None,vmin=None, vmax=None, **args):
    if ax is None or fig is None:
        ax = plt.gca()
        fig = plt.gcf()
        
    if kde:
        im = sns.kdeplot(stars[x], ax=ax, **args)
    elif y is None:
        im = ax.hist(stars[x], **args)
        ax.set_ylabel("count")
    else:
        if c is None:
            im = ax.scatter(stars[x], stars[y], s=s, vmin=vmin, vmax=vmax, alpha=alpha, **args)

        else:
            im = ax.scatter(stars[x], stars[y], c=stars[c], s=s, alpha=alpha, vmin=vmin, vmax=vmax, **args)
            if colorbar is None:
                colorbar = True
        
        ax.set_ylabel(y)
    ax.set_xlabel(x)
    
    if colorbar:
        fig.colorbar(im, ax = ax, label=c)

    return im


zone_width=0.1
def R_to_zone(r: float):
    return int(1 + np.round(r/zone_width))
def zone_to_R(zone: int):
    return (zone) * zone_width


def load_model(name):
    """Loads a vice.milkyway model output at the location name

    Parameters
    ----------
    name : str
        the name of the model to load

    Returns
    -------
    vice.multioutput file
    """
    milkyway = vice.output(name)
    milkyway.stars["abs_z"] = calculate_z(milkyway)
    milkyway.stars["R_origin"] = zone_to_R(np.array(milkyway.stars["zone_origin"]))
    milkyway.stars["R_final"] = zone_to_R(np.array(milkyway.stars["zone_final"]))
    if "[c/o]" not in milkyway.stars.keys():
        milkyway.stars["[c/o]"] = -np.array(milkyway.stars["[o/c]"])
    if "[c/n]" not in milkyway.stars.keys():
        milkyway.stars["[c/n]"] = -np.array(milkyway.stars["[n/c]"])
    return milkyway




