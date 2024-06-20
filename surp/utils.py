from functools import wraps
from numbers import Real
import requests
from astropy.table import Table
import textwrap
import os
import numpy as np
import json
from os import path
from dataclasses import dataclass, field, asdict



class AbstractParams:
    """ A general config class used for yieldparams and parameters"""
    def to_dict(self):
        return asdict(self)

    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)


    @classmethod
    def from_file(cls, filename):
        with open(filename, "r") as f:
            params = json.load(f)

        if "inherits" in params:
            parentname = params.pop("inherits")
            parentname = path.join(path.dirname(filename), parentname)
            parent = cls.from_file(parentname).to_dict()
            
            for key in parent.keys():
                if key not in params:
                    params[key] = parent[key]


        return cls(**params)

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self):
        return self.__str__()



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


def isreal(param):
    """Validates if the given parameter is real"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if param not in kwargs:
                raise ValueError(f"Parameter not in function kwargs: {param}")
            if not isinstance(kwargs[param], Real):
                raise ValueError(f"Parameter {param} must be real, got {kwargs[param]}")
                
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate(param, condition, is_real=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if param not in kwargs:
                raise ValueError(f"Parameter not in function kwargs: {param}")
            if condition(kwargs[param]):
                raise ValueError(f"validation failed for {param} = {kwargs[param]}")
                
            return func(*args, **kwargs)
        return wrapper
    return decorator


def arg_isreal(arg=0):
    """Checks if the given argument of the function is real"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            val = args[arg]
            if not isinstance(arg, Real):
                raise TypeError(f"argument must be a number, got {type(other).__name__}")
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



