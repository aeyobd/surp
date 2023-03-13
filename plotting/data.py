## Holds the data backend

import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype, is_integer_dtype

class PlotData():
    def __init__(self, x, y=None, xerr=None, yerr=None, z=None, c=None, s=None,
                 m=None, df=None):
        if df is not None:
            self.df = df

        self.length = len(x)
        self.x = x
        self.y = y
        self.z = z
        self.xerr = xerr
        self.yerr = yerr
        self.c = c
        self.s = s
        self.m = m

        self.vars = {
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "xerr": self.xerr,
                "yerr": self.yerr,
                "c": self.c,
                "s": self.s,
                "m": self.m
                }

        self._check_lens()
        self._set_columns()
        self._set_cats()

    def _check_lens(self):
        l = len(self)
        for name, var in self.vars.items():
            if var is not None:
                if len(var) != l:
                    raise ValueError("make sure all columns are the same length")

    def _set_cats(self):
        self.cats = dict(filter(lambda x: x[1]=="cat",
                                self.columns.items())).keys()
        self.cats = list(self.cats)
        self.n_cats = len(self.cats)



    def group_by(self, col):
        keys = pd.unique(self.vars[col])
        filters = {
                key: self.vars[col] == key for key in keys
                }

        return {
                key: self.filter(filt) 
                for key, filt in filters.items()
                }

    def filter(self, filt):
        new_dat = {}
        for key, ser in self.vars.items():
            if ser is None:
                new_dat[key] = None
            else:
                new_dat[key] = ser[filt]

        return PlotData(**new_dat)

    def _set_columns(self):
        names = ["x", "y", "z", "xerr", "yerr", "c", "s", "m"]

        self.columns = {}

        for name, var in self.vars.items():
            if var is None:
                col = ""
            elif self.check_cat(var):
                col = "cat"
            elif self.is_numeric(var):
                col = "num"
            else:
                raise ValueError("Invalid Column type")
            self.columns[name] = col

    def check_cat(self, arr):
        return (not self.is_numeric(arr)) or (is_integer_dtype(arr) and
                                              len(pd.unique(arr)) < 10)

    @staticmethod
    def is_numeric(arr):
        return is_numeric_dtype(arr) and (arr.dtype != pd.arrays.BooleanArray)

    @staticmethod
    def cat_eq(arr1, arr2):
        cat1 = {}
        cat2 = {}
        
        for v1, v2 in zip(arr1, arr2):
            if v1 not in cat1.keys():
                n1 = len(cat1.keys())
                cat1[v1] = n1
            else:
                n1 = cat1[v1]

            if v2 not in cat2.keys():
                n2 = len(cat2.keys())
                cat2[v2] = n2
            else:
                n2 = cat2[v2]

            if n1 != n2:
                return False

        return True


    @staticmethod
    def is_array(arr):
        return isinstance(arr, (list, tuple, pd.core.series.Series,
                                np.ndarray))

    def dat_setter(self, a):
        if a is None:
            return None
        elif type(a) == str:
            return self.df[a]
        elif isinstance(a, (int, float)):
            return np.repeat(self.length, a)
        elif self.is_array(a):
            return pd.Series(a)
        else:
            raise ValueError("Column name should be listlike or string")


    # Simple properties for dataframes
    @property
    def x(self):
        """The x-axis values of the data"""
        return self._x

    @x.setter
    def x(self, a):
        self._x = self.dat_setter(a)

    @property
    def y(self):
        """The y-axis values of the data"""
        return self._y

    @y.setter
    def y(self, a):
        self._y = self.dat_setter(a)

    @property
    def z(self):
        """The z-axis values of the data"""
        return self._z

    @z.setter
    def z(self, a):
        self._z = self.dat_setter(a)

    @property
    def c(self):
        """The color axis values of the data"""
        return self._c

    @c.setter
    def c(self, a):
        self._c = self.dat_setter(a)

    @property
    def s(self):
        """The size/width axis values of the data"""
        return self._s

    @s.setter
    def s(self, a):
        self._s = self.dat_setter(a)

    @property
    def m(self):
        """The marker/line type values of the data"""
        return self._m

    @m.setter
    def m(self, a):
        self._m = self.dat_setter(a)

    @property
    def xerr(self):
        """The x_error size of the data"""
        return self._xerr

    @xerr.setter
    def xerr(self, a):
        self._xerr = self.dat_setter(a)

    @property
    def yerr(self):
        """The y_error size of the data"""
        return self._yerr

    @yerr.setter
    def yerr(self, a):
        self._yerr = self.dat_setter(a)

    def __str__(self):
        return str(pd.DataFrame(self.vars))

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.x)
