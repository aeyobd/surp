from os import path
from functools import wraps
from numbers import Real
import textwrap

from pydantic.dataclasses import dataclass
from dataclasses import field, asdict
import numpy as np

import toml


class DataclassMeta(type):
    """Metaclass for dataclasses that also adds the dataclass decorator"""
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        dataclass(cls, kw_only=True)


class AbstractParams(metaclass=DataclassMeta):
    """ A general config class used for yieldparams and parameters"""
    def to_dict(self):
        return asdict(self)

    def save(self, filename):
        with open(filename, "w") as f:
            toml.dump(self.to_dict(), f)


    @classmethod
    def from_file(cls, filename, **kwargs):
        params = load_toml(filename)
        params = params | kwargs

        for k in params.keys():
            if k not in cls.__dataclass_fields__:
                raise ValueError(f"Unknown parameter {k} in {filename} or its parents")

        return cls(**params)

    def __str__(self):
        return toml.dumps(self.to_dict())

    def __repr__(self):
        return self.__str__()


def load_toml(filename):
    """ loads a toml file from the filename, recursavely if inherits in params"""

    with open(filename, "r") as f:
        params = toml.load(f)

    if "inherits" in params:
        parentname = params.pop("inherits")
        parentname = path.join(path.dirname(filename), parentname)
        parent = load_toml(parentname)

        params = parent | params

    return params


def get_bin_number(bins, value):
    r"""
    Returns the index of the bin in bins containing value. Returns -1 if outside the bins
    """
    for i in range(len(bins) - 1):
        if bins[i] <= value <= bins[i + 1]: return i
    return -1



def interpolate(x1, y1, x2, y2, x):
    r"""
    Extrapolate a y-coordinate for a given x-coordinate from a line defined
    by two points (x1, y1) and (x2, y2) in arbitrary units.
    """
    m = (y2 - y1) / (x2 - x1)
    return  m * (x - x1) + y1



def arg_isreal(arg=0):
    """Checks if the given argument of the function is real"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            val = args[arg]
            if not isinstance(val, Real):
                raise TypeError(f"argument must be a number, got {type(val).__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator



def arg_numpylike(arg=0):
    """casts the argument into a numpy array"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            new_args = list(args)
            if len(args) > arg:
                new_args[arg] = np.array(args[arg])

            return func(*new_args, **kwargs)
        return wrapper
    return decorator




def print_row(*args, widths=None, float_fmt="%0.2e"):
    """
    given a list of arguments, prints them in a table format
    """
    strings = []

    for i in range(len(args)):
        arg = args[i]
        if isinstance(arg, float):
            s = float_fmt % arg
        else:
            s = str(arg)
        strings.append(s)

    N = len(args)
    wrapped = [textwrap.wrap(s, width=w) for s, w in zip(strings, widths)]

    N_rows = max([len(wd) for wd in wrapped])
    padded = [wd + [''] * (N_rows - len(wd)) for wd in wrapped]

    fmt = "".join("{{:<{}}} ".format(w) for w in widths)

    for i in range(N_rows):
        print(fmt.format(*(col[i] for col in padded)))
    print()



