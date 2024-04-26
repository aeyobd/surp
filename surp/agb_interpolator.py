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
            prefactor=1, mass_factor=1, interp_kind="log",
            no_negative=False, no_negative_mass="lowest", low_z_flat=True,
            min_mass="lowest", max_mass=8):
        """
        interpolator()

        A 2-D interpolation scheme for AGB star yield data used in the Boyea et al. (2024) paper.
        Unlike default vice interpolators, this model (by default) interpolates in log metallicity (instead of linearly in metallicity) and sets yields less than the lowest sampled mass to zero. This is in order to more intuitively match the qualitative trends of the C predictions of yields.

        Parameters
        ---------
        element : str
            The element for which to interpolate yields.
        study : str
            The study from which to interpolate yields. 
            See vice options for available studies
        prefactor : float
            The multiplicative factor to apply to the interpolated yields.
        mass_factor : float
            Systematically shift yield masses?
        interp_kind : str
            The kind of interpolation to perform. 
            Options are "linear" and "log"
        min_mass : float or "lowest"
            The minimum mass with nonzero yields
        max_mass : float
            The maximum AGB mass. (hardcoded upper limit of 8 in VICE)
        low_z_flat : bool
            If True, the interpolation will be flat at the lowest metallicity. Particularlly important for log interpolation so that C AGB yields do not diverge.
        """

        yields, masses, metallicities = yield_grid(element, study = study)

        self.element = element
        self.study = study
        self.prefactor = prefactor
        self.mass_factor = mass_factor
        self.interp_kind = interp_kind
        self.no_negative = no_negative

        if no_negative_mass == "lowest":
            no_negative_mass = min(masses)
        self.no_negative_mass = no_negative_mass

        self.low_z_flat = low_z_flat

        if min_mass == "lowest":
            min_mass = min(masses)
        self.min_mass = min_mass
        self.max_mass = max_mass

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
            self._call_noneg = lambda M, y: np.where(M < no_negative_mass, max(0, y), y)
        else:
            self._call_noneg = lambda M, y: y


    def _call_linear(self, M, Z):
        return super().__call__(self.mass_factor*M, Z)

    def _call_log(self, M, Z):
        return super().__call__(self.mass_factor*M, math.log10(Z))

    def _truncate(self, M, Z):
        return (M < self.min_mass) or (M > self.max_mass)

    def __call__(self, M, Z):
        if self._truncate(M, Z):
            return 0

        M, Z = self._call_lowz(M, Z)
        y = self._call_interp(M, Z)
        y = self._call_noneg(M, y)

        return y * self.prefactor

    @property
    def masses(self):
        return super().xcoords

    @property
    def yields(self):
        return super().zcoords

    def copy(self):
        return interpolator(
            self.element, 
            study=self.study, 
            prefactor=self.prefactor, 
            mass_factor=self.mass_factor, 
            interp_kind=self.interp_kind,
            no_negative=self.no_negative,
            no_negative_mass=self.no_negative_mass,
            low_z_flat=self.low_z_flat,
            min_mass=self.min_mass,
            max_mass=self.max_mass)

    def __str__(self): 
        return f"{self.prefactor:0.2f} × {self.study}"

    def __repr__(self): 
        return str(self)

    def __mul__(self, a):
        new = self.copy()
        new.prefactor *= a
        return new
