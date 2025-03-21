from copy import copy
import re
import numpy as np

import vice

from .._globals import  MAX_RADIUS, DATA_DIR, END_TIME
from ..utils import get_bin_number, interpolate 
from . import sfh_models



class star_formation_history:
    r"""
        star_formation_history(params)

    The star formation history (SFH) of the model galaxy. This object will be
    used as the ``evolution`` attribute of the milky way model.

    Initialized from a MWParams object. 
    The object can then be called with a radius and time to return the star
    formation rate.

    Depends on:
    - params.radial_bins
    - params.max_sf_radius
    - params.r
    - params.timestep
    
    And passes parameters to:
    - normalized_gradient
    - create_sfh_model
    """

    def __init__(self, params):
        self._radii = midpoints(params.radial_bins)
        self._bins = params.radial_bins
        self._params = params
        self._create_sfhs()
        self._normalize()

    def _create_sfhs(self):
        self._evol = []

        for i in range(len(self)):
            r = self._radii[i]
            evol = create_sfh_model(r, self._params)
            self._evol.append(evol)

    def _normalize(self):
        masses = normalized_gradient(self._params)
        dt = self._params.timestep
        self._coeffs = np.ones(len(self))

        for i in range(len(self)):
            time_integral = 0
            for j in range(int(END_TIME / dt) + 1):
                t = j * dt
                time_integral += self._evol[i](t) * dt

            norm = time_integral * (1 - self._params.r)  * 1e9 # yr to Gyr
            self._coeffs[i] = masses[i] / norm

    def __call__(self, radius, time):
        # The milkyway object will always call this with a radius in the
        # self._radii array, but this ensures a continuous function of radius
        if radius > self._params.max_sf_radius:
            return 0

        if radius not in self._radii and radius != 1:
            print(f"Warning: radius {radius} not in radii array")

        idx = get_bin_number(self._bins, radius)

        if idx != -1 and idx < len(self)- 1:
            return self._coeffs[idx] * interpolate(self._radii[idx],
                self._evol[idx](time), self._radii[idx + 1],
                self._evol[idx + 1](time), radius)
        else:
            return self._coeffs[idx] * interpolate(self._radii[-2],
                self._evol[-2](time), self._radii[-1], self._evol[-1](time),
                radius)

    def __len__(self):
        return len(self._radii)

    def __str__(self):
        return f"{self._params.sfh_model}"

    def __repr__(self):
        return str(self)



def create_sfh_model(radius, params): 
    """
    create_sfh_model(radius, params)

    Create a star formation history model at a given radius given the
    MWParams object.

    Returns subclass of SFHModel.

    Replaces values of `sanchez` in kwargs with the appropriate timescale for the radius (muplitiplied by a number if there is a float in the string.

    For the twoinfall model only, the A2 parameter is additionally scaled by the 
    local thin/thick ratio relative to solar.

    Depends on:
    - params.sfh_model
    - params.sfh_kwargs
    - params.Re
    - params.thin_disk_scale_radius
    - params.thick_disk_scale_radius
    - params.thin_to_thick_ratio
    - params.r_sun

    """

    tau_sfh = get_sfh_timescale(radius, Re = params.Re)

    kwargs = copy(params.sfh_kwargs)
    for key, val in kwargs.items():
        if val == "sanchez":
            kwargs[key] = tau_sfh
        elif type(val) == str and "sanchez" in val:
            factor = re.findall(r'[-+]?(?:\d*\.*\d+)', val)[0]
            kwargs[key] = tau_sfh * float(factor)

    name = params.sfh_model
    if name == "insideout":
        sfh = sfh_models.insideout(**kwargs)
    elif name == "lateburst":
        sfh = sfh_models.lateburst(**kwargs)
    elif name == "exp":
        sfh = sfh_models.exp_sfh(**kwargs)
    elif name == "twoexp":
        sfh = sfh_models.twoexp(**kwargs)
    elif name == "twoinfall":
        t_T = params.thin_to_thick_ratio
        r_t = params.thin_disk_scale_radius
        r_T = params.thick_disk_scale_radius
        r_sun = params.r_sun

        At = np.exp(-(radius - r_sun) / r_t)
        AT = np.exp(-(radius - r_sun) / r_T)
        kwargs["A2"] = kwargs["A2"] * At/AT  * t_T
        sfh = sfh_models.twoexp(**kwargs)

    elif name == "linexp":
        sfh = sfh_models.linexp(**kwargs)
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
    tau_min = 1
    radius /= Re # convert to units of Re
    radii, timescales = _read_sanchez_data()
    idx = get_bin_number(radii, radius)
    if idx != -1:
        return interpolate(radii[idx], timescales[idx], radii[idx + 1],
            timescales[idx + 1], radius) 
    else:
        return max(tau_min, interpolate(radii[-2], timescales[-2], radii[-1],
            timescales[-1], radius) )






def BG16_stellar_density(radius, params):
    r"""
    BG16_stellar_density(radius, params)

    The gradient in stellar surface density defined in Bland-Hawthorn &
    Gerhard (2016) [1]_.

    Depends on
    - params.thin_disk_scale_radius
    - params.thick_disk_scale_radius
    - params.thin_to_thick_ratio
    
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
    A_thin = params.thin_to_thick_ratio
    return A_thin * np.exp(-radius / R_thin) + np.exp(-radius / R_thick)


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
    """
    normalized_gradient(params, gradient=BG16_stellar_density)


    Returns the normalized gradient of the stellar surface density profile,
    i.e. the mass gradient in each bin.

    gradient is a function accepting the radius and params as arguments, 
    returning the 2D surface density at the radius.

    Depends on:
    - params.radial_bins
    - params.max_sf_radius
    - params.M_star_MW
    """
    radial_bins = np.array(params.radial_bins)

    radii = midpoints(radial_bins)
    unnorm = gradient(radii, params)
    unnorm = np.where(radii > params.max_sf_radius, 0, unnorm)

    areas = np.pi * delta(radial_bins**2)
    radius_integral = np.sum(unnorm * areas)

    return params.M_star_MW / radius_integral * unnorm


def midpoints(array):
    """
    midpoints(array)

    Returns the midpoints of each consecutive pair of elements in the input.
    """
    a = np.array(array)
    return 1/2*(a[1:] + a[:-1])


def delta(array):
    """
    delta(array)

    Returns the difference between each consecutive pair of elements in the
    input.
    """
    a = np.array(array)
    return a[1:] - a[:-1]

