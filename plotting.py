import matplotlib.pyplot as plt
import numpy as np
from functools import wraps

class fig_saver():
    def __init__(self, output_dir = ".", show=True):
        self.show = show
        if output_dir[-1] == "/":
            self.output_dir = output_dir
        else:
            self.output_dir = output_dir + "/"

    def save(self, name):
        plt.savefig(self.output_dir + name + ".pdf")
        plt.savefig(self.output_dir + name + ".jpeg")
        if self.show:
            plt.show()

    def __call__(self, name):
        self.save(name)




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
def density_scatter(x, y, xlim=None, ylim=None, n_bins=100, fig=None, ax=None, **kwargs):
    if xlim is None:
        xlim = (min(x), max(x))
    if ylim is None:
        ylim = (min(y), max(y))

    if fig is None or ax is None:
        fig, ax = plt.subplots()

    x_bins = np.linspace(xlim[0], xlim[1], n_bins)
    y_bins = np.linspace(ylim[0], ylim[1], n_bins)


    f = ax.hist2d(x, y, bins=[x_bins, y_bins], cmin=1, density=True)

    fig.colorbar(f, label="Density", ax=ax)
    return f

