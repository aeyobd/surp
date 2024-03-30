r"""
ReImplement the vice.yields.agb.interpolator, which constructs a 2-D linear
interpolation scheme off of the built-in yield sets.
"""

from vice.toolkit.interpolation.interp_scheme_2d import interp_scheme_2d
from vice.yields.agb._grid_reader import yield_grid
import math
import numpy as np
from scipy.interpolate import CubicSpline



class interpolator(interp_scheme_2d):
    def __init__(self, element, study="cristallo11", 
              prefactor=1, mass_factor=1, interp_kind="linear",
              no_negative=False, low_z_flat=False):
        # let the grid reader function do the error handling
        yields, masses, metallicities = yield_grid(element, study = study)
        self._nonegative = no_negative
        self.element = element

        if no_negative:
            yields = [[max(0, a) for a in b] for b in yields]
        self.study=study
        self.interp_kind = interp_kind
        self.mass_factor = mass_factor
        self.no_negative = no_negative
        self.prefactor=prefactor
        self.low_z_flat = low_z_flat
        self.metallicities = metallicities

        if interp_kind == "linear":
            super().__init__(list(masses), list(metallicities), list(yields))
            self._call_interp = self._call_linear

        elif interp_kind == "log":
            super().__init__(
                    list(masses), 
                    [math.log10(z) for z in metallicities], 
                    list(yields))
            self._call_interp = self._call_log
        else:
            raise ValueError("unexpected interp_kind: %s" % interp_kind)

        if self.low_z_flat:
            self._call_lowz = lambda M, Z: (M, max(Z, self.metallicities[0]))
        else:
            self._call_lowz = lambda M, Z: (M, Z)

        if self.no_negative:
            self._call_noneg = lambda y: max(0, y)
        else:
            self._call_noneg = lambda y: y


    def _call_linear(self, M, Z):
        return super().__call__(self.mass_factor*M, Z)

    def _call_log(self, M, Z):
        return super().__call__(self.mass_factor*M, math.log10(Z))


    def __call__(self, M, Z):
        M, Z = self._call_lowz(M, Z)
        y = self._call_interp(M, Z)
        y = self._call_noneg(y)

        return y * self.prefactor

    @property
    def masses(self):
        return super().xcoords

    @property
    def yields(self):
        return super().zcoords

    def copy(self):
        return interpolator(self.element, study=self.study, prefactor=self.prefactor, mass_factor=self.mass_factor, interp_kind = self.interp_kind, no_negative=self.no_negative, low_z_flat=self.low_z_flat)

    def __str__(self): 
        return f"{self.prefactor:0.2f} × {self.study}"

    def __repr__(self): 
        return str(self)

    def __mul__(self, a):
        new = self.copy()
        new.prefactor *= a
        return new
