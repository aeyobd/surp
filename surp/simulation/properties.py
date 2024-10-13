import numpy as np

import vice
from vice.toolkit import J21_sf_law

try:
    from vice.toolkit.rand_walk.rand_walk_stars import rand_walk_stars 
    from vice.toolkit.analytic_migration.analytic_migration_2d import analytic_migration_2d
except ImportError:
    print("modified vice not installed, fancy migration not available")

from vice.toolkit.hydrodisk.hydrodiskstars import hydrodiskstars 

from .star_formation_history import star_formation_history 
from ..yields import set_yields
from .._globals import Z_SUN
from surp.yield_models import chabrier



def set_sf_law(model, params):
    for zone in model.zones:
       zone.Mg0 = 0.
    
    tot_area = 0  # sanity check for me

    for i in range(model.n_zones):
        R1 = model.annuli[i]
        R2 = model.annuli[i+1]
        R = (R1 + R2)/2
        area = np.pi * (R2**2 - R1**2)
        tot_area += area
        if R <= params.max_sf_radius:

            if params.sf_law == "conroy22":
                model.zones[i].tau_star = conroy_sf_law(area)
            elif params.sf_law == "twoinfall":
                kwargs = params.sfh_kwargs
                model.zones[i].tau_star = twoinfall_sf_law(area,
                    nu1=kwargs["nu1"], nu2=kwargs["nu2"], t1=kwargs["t1"]
                    )
            elif params.sf_law == "J21":
                model.zones[i].tau_star = J21_sf_law(area, mode="sfr", present_day_molecular=params.tau_star0)
            else:
                raise ValueError("SF law not known ", params.sf_law)

    tot_area_exp = np.pi * (model.annuli[-1]**2 - model.annuli[0]**2)
    relerr = abs(tot_area - tot_area_exp) / tot_area_exp
    assert relerr < 1e-3, f"Area {tot_area} does not match expected {tot_area_exp} within 1e-3"



def conroy_tau_star(t):
    if t < 2.5:
        tau_st = 50
    elif 2.5 <= t < 3.7:
        tau_st = 50/(1+3*(t-2.5))**2
    else:
        tau_st = 2.36
    return tau_st


def conroy_sf_law(area=None):
    def inner(t):
        tau_st = conroy_tau_star(t)
        return tau_st #J21_sf_law(area, tau_st)(t, m)
    return inner


def twoinfall_sf_law(area=None, t1=4.1, nu1=2, nu2=1):
    def inner(t, m):
        tau_st = twoinfall_tau_star(t, t1, nu1, nu2)
        return tau_st
    return inner
    

def twoinfall_tau_star(t, t1, nu1, nu2):
    """
        twoinfall_tau_star(t, t1, nu1, nu2)

    Returns the star formation timescale at time t for a two-infall model.

    Parameters
    ----------
    t1: time of transition
    nu1: star formation efficienty before transition
    nu2: star formation efficiency after transition

    Returns
    -------
    tau_star: float
        The star formation timescale at time t. (1/nu)
    """
    if t < t1:
        return 1/nu1
    else:
        return 1/nu2


def create_migration(bins, params):
    kind = params.migration
    if params.save_migration:
        filename="star_migration.dat"
    else:
        filename = None

    if kind == "rand_walk":
        migration = rand_walk_stars(bins, n_stars=params.n_stars, dt=params.timestep, 
            name=filename, sigma_R=params.sigma_R
            )
    elif kind == "gaussian":
        migration = analytic_migration_2d(
            bins, 
            dt=params.timestep, 
            n_stars=params.n_stars, 
            filename=filename, 
            verbose=params.verbose,
            initial_final_filename="migration_initial_final.dat",
        )
    elif kind == "hydrodisk":
        migration = hydrodiskstars(bins, N=params.N_star_tot)
    else:
        raise ValueError("migration mode not known", kind)

    return migration



class MH_grad:
    def __init__(self, params):
        """Metallicity gradient of galaxy from Hayden et al. 2014"""
        self.R0 = params.MH_grad_R0
        self.MH_0 = params.MH_grad_MH0
        self.zeta_in = params.MH_grad_in
        self.zeta_out = params.MH_grad_out

    def __call__(self, R):
        return self.MH_0 + (R-self.R0) * np.where(R<self.R0, self.zeta_in, self.zeta_out)

    def __str__(self):
        s =  f"{self.MH_0:0.2f} + {self.zeta_in}(R-{self.R0}) , R > {self.R0}"
        s += "; "
        s +=  f"{self.MH_0:0.2f} + {self.zeta_out}(R-{self.R0}) , R < {self.R0}"
        return s


class mass_loading:
    """A class which represents the mass loading profile of galaxy. Set yields before calling this
    params.eta_scale scales the assumed yield setting used here. approximantly multiplies eta by this value
    params.r is the approximated return fraction
    params.tau_star_sfh_grad is the linear approximation of tau_star / tau_sfh ~ R.
    """
    def __init__(self, params):
        r = params.r
        yo = vice.yields.ccsne.settings["o"] * params.eta_scale

        self.B = params.r - 1
        self.C = yo / vice.solar_z("o") 

        self.MH_func = MH_grad(params)
        self.tau_star_sfh_grad = params.tau_star_sfh_grad

    def __call__(self, R_gal):
        MH = self.MH_func(R_gal)
        eta = self.B + self.C * 10**-MH + self.tau_star_sfh_grad * R_gal
        return np.maximum(0, eta)

    def __str__(self):
        s = f"{self.B:0.4f} + {self.C:0.4f}×10^[M/H];\r\t\t\t [M/H] = {self.MH_func}"
        return s

    def __repr__(self):
        return str(self)


def get_imf(params):
    if params.imf == "salpeter":
        return params.imf
    elif params.imf == "kroupa":
        return params.imf
    elif params.imf == "chabrier":
        return chabrier
    else:
        raise ValueError("IMF not known", params.imf)


