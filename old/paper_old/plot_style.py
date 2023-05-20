import matplotlib as mpl
import matplotlib.style as style 
import matplotlib.pyplot as plt
import inspect
from os import path
from mpl_toolkits.axes_grid1 import Divider, Size


def init():
    style.use("./journal.mplstyle")
    # style.use('seaborn-colorblind')
    mpl.ticker.AutoLocator.__init__ = AutoLocatorInit

def AutoLocatorInit(self):
    mpl.ticker.MaxNLocator.__init__(self,
            nbins = "auto",
            steps = [1,2,5,10])

def save():
    filename = inspect.stack()[1].filename

    base, ext = path.splitext(filename)
    dir_path, name = path.split(base)

    save_folder = "./figures/"

    save_name = path.join(dir_path, save_folder, name)

    options = {
               "bbox_inches": "tight"
              }

    plt.savefig(save_name + ".pdf", **options)
    plt.savefig(save_name + ".jpeg", **options)
    print("saving ", base)

    clear()

def clear():
    plt.clf()
    mpl.rcParams.update(mpl.rcParamsDefault)
    style.use("./journal.mplstyle")
    plt.style.reload_library()

def double_fig():
    fig = plt.figure(figsize=(3,3))
    h = [Size.Fixed(1.), Size.Fixed(WIDTH)]
    v = [Size.Fixed(1.), Size.Fixed(WIDTH)]
    divider = Divider(fig, (0,0,1,1), h, v)
    ax = fig.add_axes(divider.get_position(),
                      axes_locator=divider.new_locator(nx=1,ny=1))

    return fig, ax

def get_plot():
    fig = plt.figure(figsize=(3,3))
    h = [Size.Fixed(1.), Size.Fixed(WIDTH)]
    v = [Size.Fixed(1.), Size.Fixed(WIDTH)]
    divider = Divider(fig, (0,0,1,1), h, v)
    ax = fig.add_axes(divider.get_position(),
                      axes_locator=divider.new_locator(nx=1,ny=1))

    return fig, ax


init()

WIDTH = 2.362 #inches
COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']
