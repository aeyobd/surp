from .._globals import  MAX_RADIUS, DATA_DIR, END_TIME
from ..utils import get_bin_number, interpolate 
from . import sfh_models

import numpy as np
import math as m
import vice



def create_sfh_model(radius, params): 
    tau_sfh = get_sfh_timescale(radius)

    name = params.sfh_model
    if name == "insideout":
        sfh = sfh_models.insideout(radius, 
           tau_rise=params.tau_rise, tau_sfh=tau_sfh)
    elif name == "lateburst":
        sfh = sfh_models.lateburst(radius)
    elif name == "static":
        sfh = sfh_models.static
    else:
        raise ValueError("unknown SFH: ", name)

    normalize_sfh(sfh, radius, params)
    return sfh



class star_formation_history:
    r"""
    The star formation history (SFH) of the model galaxy. This object will be
    used as the ``evolution`` attribute of the milky way model.
    """

    def __init__(self, params):
        self._radii = np.arange(params.zone_width/2, MAX_RADIUS, params.zone_width) # maybe _get_radial_bins instead
        self._evol = [create_sfh_model(r, params) for r in self._radii]
        self._max_sf = params.max_sf_radius
        self.sfh_model = params.sfh_model
        self._params = params

    def __call__(self, radius, time):
        # The milkyway object will always call this with a radius in the
        # self._radii array, but this ensures a continuous function of radius
        if radius > self._max_sf:
            return 0

        idx = get_bin_number(self._radii, radius)

        if idx != -1:
            return BG16_stellar_density(radius, self._params) * interpolate(self._radii[idx],
                self._evol[idx](time), self._radii[idx + 1],
                self._evol[idx + 1](time), radius)
        else:
            return BG16_stellar_density(radius, self._params) * interpolate(self._radii[-2],
                self._evol[-2](time), self._radii[-1], self._evol[-1](time),
                radius)


    def __str__(self):
        return f"{self.sfh_model}"

    def __repr__(self):
        return str(self)



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
    return m.exp(-radius / R_thin) + A_thick * m.exp(-radius / R_thick)


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


def normalize_sfh(sfh_model, radius, params, radial_gradient=BG16_stellar_density):
    dt = params.timestep
    dr = params.zone_width

    time_integral = 0
    for i in range(int(END_TIME / dt)):
        time_integral += sfh_model(i * dt) * dt * 1.e9 # yr to Gyr

    radial_integral = 0
    for i in range(int(params.max_sf_radius / dr)):
        r = dr * (i + 1/2)
        radial_integral += radial_gradient(r, params) * m.pi * (
            (dr * (i + 1))**2 - (dr * i)**2
        )

    return params.M_star_MW / ((1 - params.r) * radial_integral * time_integral)
