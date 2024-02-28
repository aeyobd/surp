import numpy as np

import vice
from vice.toolkit import J21_sf_law
from vice.milkyway.milkyway import _get_radial_bins
#from vice.toolkit.rand_walk.rand_walk_stars import rand_walk_stars 
from vice.toolkit.gaussian.gaussian_stars import gaussian_stars 
from vice.toolkit.hydrodisk.hydrodiskstars import hydrodiskstars 

from .star_formation_history import star_formation_history 
from ..yields import set_yields
from .._globals import Z_SUN


def create_model(params):
    """"
    This function wraps various settings to make running VICE multizone models
    easier for the carbon paper investigation
    """

    model = vice.milkyway(zone_width=params.zone_width,
            name = params.filename,
            n_stars=params.n_stars,
            N=params.N_star_tot,
            simple=params.simple,
            migration_mode=params.migration_mode,
            )

    model.elements = ("fe", "o", "mg", "n", "c")
    model.dt = params.timestep
    model.bins = np.arange(-3, 3, 0.01) # don't use this so is okay
    model.RIa = params.RIa
    model.Z_solar = Z_SUN

    model.evolution = star_formation_history(params)
    set_sf_law(model, params)
    model.migration.stars = create_migration(params)
    model.mass_loading = mass_loading(params)

    return model


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



def MH_grad(R, R0=5, MH_0 = 0.29, zeta_in=-0.15, zeta_out=-0.09):
    """Metallicity gradient of galaxy from Hayden et al. 2014"""
    return MH_0 + (R-R0) * np.where(R<R0, zeta_in, zeta_out)


class mass_loading:
    """A class which represents the mass loading profile of galaxy"""
    def __init__(self, params):
        self._factor = params.yield_scale
        r = params.r
        yo = self._factor * vice.yields.ccsne.settings["o"]

        self.B = params.r - 1
        self.C = yo / vice.solar_z("o") 

    def __call__(self, R_gal):
        MH = MH_grad(R_gal)
        eta = self.B + self.C * 10**MH
        return np.maximum(0, eta)

    def __str__(self):
        s = f"{self.B} + {self.C}×10^([M/H]); MH = str"
        return s

    def __repr__(self):
        return str(self)
