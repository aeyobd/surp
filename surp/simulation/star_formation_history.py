from copy import copy
import numpy as np

import vice

from .._globals import  MAX_RADIUS, DATA_DIR, END_TIME
from ..utils import get_bin_number, interpolate 
from . import sfh_models



class star_formation_history:
    r"""
    The star formation history (SFH) of the model galaxy. This object will be
    used as the ``evolution`` attribute of the milky way model.
    """

    def __init__(self, params):
        self._radii = midpoints(params.radial_bins)
        self._params = params
        self.create_sfhs()
        self.normalize()


    def create_sfhs(self):
        self._evol = []

        for i in range(len(self)):
            r = self._radii[i]
            evol = create_sfh_model(r, self._params)
            self._evol.append(evol)

    def normalize(self):
        masses = normalized_gradient(self._params)
        dt = self._params.timestep
        self._coeffs = np.ones(len(self))

        for i in range(len(self)):
            time_integral = 0
            for j in range(int(END_TIME / dt)):
                t = j * dt
                time_integral += self._evol[i](t) * dt * 1.e9 # yr to Gyr
            self._coeffs[i] = masses[i] / (time_integral * (1 - self._params.r))


    def __len__(self):
        return len(self._radii)

    def __call__(self, radius, time):
        # The milkyway object will always call this with a radius in the
        # self._radii array, but this ensures a continuous function of radius
        if radius > self._params.max_sf_radius:
            return 0

        idx = get_bin_number(self._radii, radius)

        if idx != -1:
            return self._coeffs[idx] * interpolate(self._radii[idx],
                self._evol[idx](time), self._radii[idx + 1],
                self._evol[idx + 1](time), radius)
        else:
            return self._coeffs[idx] * interpolate(self._radii[-2],
                self._evol[-2](time), self._radii[-1], self._evol[-1](time),
                radius)


    def __str__(self):
        return f"{self._params.sfh_model}"

    def __repr__(self):
        return str(self)



def create_sfh_model(radius, params): 
    tau_sfh = get_sfh_timescale(radius)

    kwargs = copy(params.sfh_kwargs)
    for key, val in kwargs.items():
        if val == "sanchez":
            kwargs[key] = tau_sfh

    print(kwargs)
    name = params.sfh_model
    if name == "insideout":
        sfh = sfh_models.insideout(**kwargs)
    elif name == "lateburst":
        sfh = sfh_models.lateburst(**kwargs)
    elif name == "static":
        sfh = sfh_models.static()
    else:
        raise ValueError("unknown SFH: ", name)

    return sfh


def get_sfh_timescale(radius, Re = 5):
    r"""
    Determine the timescale of star formation at a given radius reported
    by Sanchez (2020) [1]_.

    Parameters
    ----------
    radius : real number
        Galactocentric radius in kpc.
    Re : real number [default : 5]
        The effective radius (i.e. half-mass radius) of the galaxy in kpc.

    Returns
    -------
    tau_sfh : real number
        The e-folding timescale of the star formation history at that
        radius. The detailed time-dependence on the star formation history
        has the following form:

        .. math:: \dot{M}_\star \sim
            (1 - e^{-t / \tau_\text{rise}})e^{-t / \tau_\text{sfh}}

        where :math:`\tau_\text{rise}` = 2 Gyr and :math:`\tau_\text{sfh}`
        is the value returned by this function.

    .. [1] Sanchez (2020), ARA&A, 58, 99
    """
    radius /= Re # convert to units of Re
    radii, timescales = _read_sanchez_data()
    idx = get_bin_number(radii, radius)
    if idx != -1:
        return interpolate(radii[idx], timescales[idx], radii[idx + 1],
            timescales[idx + 1], radius) 
    else:
        return interpolate(radii[-2], timescales[-2], radii[-1],
            timescales[-1], radius) 



def midpoints(array):
    a = np.array(array)
    return 1/2*(a[1:] + a[:-1])


def delta(array):
    a = np.array(array)
    return a[1:] - a[:-1]




def BG16_stellar_density(radius, params):
    r"""
    The gradient in stellar surface density defined in Bland-Hawthorn &
    Gerhard (2016) [1]_.
    
    Parameters
    ----------
    radius : real number
        Galactocentric radius in kpc.
    
    Returns
    -------
    sigma : real number
        The radial surface density at that radius defined by the following
        double-exponential profile:
    
        .. math:: \Sigma_\star(r) = e^{-r/r_t} + Ae^{-r/r_T}
    
        where :math:`r_t` = 2.5 kpc is the scale radius of the thin disk,
        :math:`r_T` = 2.0 kpc is the scale radius of the thick disk, and
        :math:`A = \Sigma_T / \Sigma_t \approx` 0.27 is the ratio of thick to
        thin disks at :math:`r = 0`.
    
        .. note:: This gradient is un-normalized.

    .. [1] Bland-Hawthorn & Gerhard (2016), ARA&A, 54, 529
    """

    R_thin = params.thin_disk_scale_radius
    R_thick = params.thick_disk_scale_radius
    A_thick = params.thin_to_thick_ratio
    return np.exp(-radius / R_thin) + A_thick * np.exp(-radius / R_thick)


def _read_sanchez_data():
    r"""
    Reads the Sanchez (2020) [1]_ star formation timescale data.

    Returns
    -------
    radii : list
        Radius in units of the effective radius :math:`R_e` (i.e. the
        half-mass radius).
    timescales : list
        The star formation timescales in Gyr associated with each effective
        radius.

    .. [1] Sanchez (2020), ARA&A, 58, 99
    """
    radii = []
    timescales = []

    filename = f"{DATA_DIR}/sanchez_tau_sfh.dat"
    with open(filename, 'r') as f:

        line = f.readline()
        
        # read past the header
        while line[0] == '#':
            line = f.readline()

        # pull in each line until end of file is reached
        while line != "":
            line = [float(i) for i in line.split()]
            radii.append(line[0])
            timescales.append(line[1])
            line = f.readline()

        f.close()
    return [radii, timescales]


def normalized_gradient(params, gradient=BG16_stellar_density):
    radial_bins = np.array(params.radial_bins)

    radii = midpoints(radial_bins)
    unnorm = gradient(radii, params)
    unnorm = np.where(radii > params.max_sf_radius, 0, unnorm)

    areas = np.pi * (radial_bins[1:]**2 - radial_bins[:-1]**2)
    radius_integral = np.sum(unnorm * areas)

    return params.M_star_MW / radius_integral * unnorm
