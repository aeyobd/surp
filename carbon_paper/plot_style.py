import matplotlib as mpl
import matplotlib.style as style 
import matplotlib.pyplot as plt
import inspect
from os import path


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

init()

COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']
WIDTH = 3.15 #inches
