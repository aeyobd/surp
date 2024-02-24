from .. import _globals
from vice.milkyway.milkyway import _get_radial_bins
#from vice.toolkit.rand_walk.rand_walk_stars import rand_walk_stars 
from vice.toolkit.gaussian.gaussian_stars import gaussian_stars 
from vice.toolkit.hydrodisk.hydrodiskstars import hydrodiskstars 
import vice
import numpy as np
from vice.toolkit import J21_sf_law


def set_sf_law(model, params):
    for zone in model.zones:
       zone.Mg0 = 0.

    for i in range(model.n_zones):
        R1 = model.annuli[i]
        R2 = model.annuli[i+1]
        R = (R1 + R2)/2

        if R <= params.max_sf_radius:
            area = np.pi * (R2**2 - R1**2)
            if params.sf_law == "conroy22":
                model.zones[i].tau_star = conroy_sf_law(area)
            elif params.sf_law == "two_infall":
                model.zones[i].tau_star = twoinfall_sf_law(area)
            elif params.sf_law == "J21":
                model.zones[i].tau_star = J21_sf_law(area, mode="sfr")
            else:
                raise ValueError("SF law not known ", params.sf_law)


def conroy_tau_star(t):
    if t < 2.5:
        tau_st = 50
    elif 2.5 <= t < 3.7:
        tau_st = 50/(1+3*(t-2.5))**2
    else:
        tau_st = 2.36
    return tau_st


def conroy_sf_law(area=None):
    def inner(t, m):
        tau_st = conroy_tau_star(t)
        return vice.toolkit.J21_sf_law(area, tau_st)(t, m)
    return inner


def twoinfall_sf_law(area=None):
    def inner(t, m):
        tau_st = twoinfall_tau_star(t)
        return vice.toolkit.J21_sf_law(area, tau_st)(t, m)
    return inner
    

def twoinfall_tau_star(t):
    if t < 4.1:
        return 1
    else:
        return 2


def create_migration(params):
    bins = _get_radial_bins(params.zone_width)

    kind = params.migration
    kwargs = dict(n_stars=params.n_stars, dt=params.timestep, 
        name=kind, sigma_R=params.sigma_R
        )

    if kind == "rand_walk":
        migration = rand_walk_stars(bins, **kwargs)
    elif kind == "gaussian":
        migration = gaussian_stars(bins, **kwargs)
    elif kind == "hydrodisk":
        migration = hydrodiskstars(bins, N=params.N_star_tot)
    else:
        raise ValueError("migration mode not known", kind)

    return migration



def MH_grad(R):
    """Metallicity gradient of galaxy from Hayden et al. 2014"""
    R0 = 5
    return 0.29 + (R-R0) * np.where(R<R0, -0.015, -0.090)


class mass_loading:
    """A class which represents the mass loading profile of galaxy"""
    def __init__(self, params):
        self._factor = params.yield_scale
        self.r = params.r
        self.yo = self._factor * vice.yields.ccsne.settings["o"]

    def __call__(self, R_gal):
        Zo = vice.solar_z("o")*10**MH_grad(R_gal)
        return np.maximum(0,
                -1 + self.r  
                + self.yo / Zo
               )

    def __str__(self):
        A = self._factor * vice.yields.ccsne.settings["o"]/vice.solar_z("o") * 10**(-0.3 + 0.08*(-4))
        C = -0.6 * self._factor
        r = 0.08
        s = f"{C} + {A:0.4f}×10^({r:0.4f} R)"
        return s

    def __repr__(self):
        return str(self)

