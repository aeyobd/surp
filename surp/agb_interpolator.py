r"""
ReImplement the vice.yields.agb.interpolator, which constructs a 2-D linear
interpolation scheme off of the built-in yield sets.
"""

from vice.toolkit.interpolation.interp_scheme_2d import interp_scheme_2d
from vice.yields.agb._grid_reader import yield_grid
import math
from scipy.interpolate import CubicSpline



class interpolator(interp_scheme_2d):
    def __init__(self, element, study="cristallo11", 
              prefactor=1, mass_factor=1, interp_kind="linear",
              no_negative=False):
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

        if interp_kind == "linear":
            super().__init__(list(masses), list(metallicities), list(yields))
        elif interp_kind == "log":
            super().__init__(
                    list(masses), 
                    [math.log10(z) for z in metallicities], 
                    list(yields))
        else:
            raise ValueError("unexpected interp_kind: %s" % interp_kind)

    def __call__(self, M, Z):
        y = 0
        if self.interp_kind == "linear":
            y =  super().__call__(self.mass_factor*M, Z)
        elif self.interp_kind == "log":
            y =  super().__call__(self.mass_factor*M, math.log10(Z))
        if self._nonegative:
            y =  max(y, 0)

        return y * self.prefactor

    @property
    def masses(self):
        return super().xcoords

    @property
    def metallicities(self):
        return super().ycoords

    @property
    def yields(self):
        return super().zcoords

    def copy(self):
        return interpolator(self.element, study=self.study, prefactor=self.prefactor, mass_factor=self.mass_factor, interp_kind = self.interp_kind, no_negative=self.no_negative)

    def __str__(self): 
        return f"{self.prefactor:0.2f} × {self.study}"

    def __repr__(self): 
        return str(self)

    def __mul__(self, a):
        new = self.copy()
        new.prefactor *= a
        return new
