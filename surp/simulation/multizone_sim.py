# coding=utf-8
import sys
import gc
import os

import numpy as np

import vice
from vice.toolkit.rand_walk.rand_walk_stars import rand_walk_stars 
from vice.toolkit.gaussian.gaussian_stars import gaussian_stars 
from vice.toolkit.hydrodisk.hydrodiskstars import hydrodiskstars
from vice.milkyway.milkyway import _get_radial_bins


from .star_formation_history import star_formation_history
from .. import yields
from ..yields import set_yields
from .._globals import MAX_SF_RADIUS, END_TIME, N_MAX, ZONE_WIDTH


def run_model(filename, save_dir=None, 
              eta=1,
              agb_model="C11",
              timestep=0.01,
              seed=None, # needs implemented
              yield_kwargs={},
              **kwargs
     ):
    """
    This function wraps various settings to make running VICE multizone models
    easier for the carbon paper investigation
    
    Parameters
    ----------
    filename: ``str``
        The name of the model

    save_dir: ``str`` [default: None]
        The directory to save the model in
        If None, then use the argument passed to this script

    eta: ``float`` [default: 1]
        The prefactor for mass-loading strength

    agb_model: ``str`` [default: C11]
        The AGB model to use for yields. 
        - C11
        - K10 
        - V13
        - K16
        - A: Custom analytic model, see ``surp/yields.py``
        
    timestep: ``float`` [default: 0.01]
        The timestep of the simulation, measured in Gyr.
        Decreasing this value can significantly speed up results

    yield_kwargs: dict 
        kwargs passed to set_yields in ``surp/yields.py``

    migration_mode: ``str``
        Default value: diffusion
        The migration mode for the simulation. 
        Can be one of diffusion (most physical), linear, post-process, ???

    spec: ``str`` [default: "insideout"]
        The star formation specification. 
        Accepable values are
        - "insideout"
        - "constant"
        - "lateburst"
        - "outerburst"
        - "twoexp"
        - "threeexp"
        see vice.migration.src.simulation.disks.star_formation_history

    n_stars: ``int`` [default: 2]
        The number of stars to create during each timestep of the model.


    burst_size: ``float`` [default: 1.5]
        The size of the SFH burst for lateburst model.

    eta_factor: ``float`` [default: 1]
        A factor by which to reduce the model's outflows. 

    """
    print("initialized")

    # collects the first argument of the command as the directory to write
    # the simulation output to
    # this allows OSC to use the temperary directory
    if save_dir is None:
        save_dir = sys.argv[1]

    agb_model = {
            "C11": "cristallo11",
            "K10": "karakas10",
            "V13": "ventura13",
            "K16": "karakas16",
            "P16": "pignatari16",
            "A": "A"
            }[agb_model]

    set_yields(eta=eta, agb_model=agb_model, **yield_kwargs)

    print("configured yields")

    model = create_model(save_dir=save_dir, filename=filename, 
            timestep=timestep, eta=eta, **kwargs)

    print(model)

    model.run(np.arange(0, END_TIME, timestep), overwrite=True, pickle=True)

    print("finished")



def create_model(save_dir, filename, timestep,
        n_stars=2, 
        spec="insideout",
        eta=1, 
        migration_mode="diffusion", 
        lateburst_amplitude=1,
        n_threads=1, 
        sigma_R=1.27, 
        verbose=False,
        conroy_sf=False):

    if migration_mode == "post-process":
        simple = True
        migration_mode = "diffusion"
    else:
        simple = False


    Nstars = 2*MAX_SF_RADIUS/ZONE_WIDTH * END_TIME/timestep * n_stars
    if migration_mode != "rand_walk" and Nstars > N_MAX:
        Nstars = N_MAX

    print("using %i stars particles" % Nstars)


    model = vice.milkyway(zone_width=ZONE_WIDTH,
            name=save_dir + filename,
            n_stars=n_stars,
            verbose=verbose,
            N = Nstars,
            simple=simple,
            migration_mode=migration_mode
            )

    model.elements = ("fe", "o", "mg", "n", "c")
    if spec == "twoinfall" or spec=="conroy22":
        model.mode = "ifr"
    else:
        model.mode = "sfr"
    model.dt = timestep
    model.bins = np.arange(-3, 3, 0.01)
    model.setup_nthreads = n_threads
    model.nthreads = min(len(model.elements), n_threads)
            
    model.evolution = create_evolution(spec=spec, burst_size=lateburst_amplitude)

    create_sf_law(model, conroy_sf=conroy_sf, spec=spec)

    if migration_mode == "rand_walk":
        model.migration.stars = rand_walk_stars(
                _get_radial_bins(ZONE_WIDTH),
                n_stars=n_stars, 
                dt=timestep, 
                name=model.name, 
                sigma_R=sigma_R)
    elif migration_mode == "gaussian":
        model.migration.stars = gaussian_stars(
                _get_radial_bins(ZONE_WIDTH),
                n_stars=n_stars, 
                dt=timestep, 
                name=model.name, 
                sigma_R=sigma_R)


    model.mass_loading = mass_loading()

    return model




def create_evolution(spec, burst_size):
    if spec == "lateburst":
        evolution = star_formation_history(spec = spec,
                burst_size = 1.5*burst_size)
    elif spec == "twoexp":
        evolution = star_formation_history(spec = spec,
                tau2=2,
                A21 = burst_size,
                )
    elif spec == "twoinfall":
        evolution = star_formation_history(spec=spec,
                tau1=2,
                A21 = 3.5 * burst_size,
                )
    elif spec == "threeexp":
        evolution = star_formation_history(
                spec = spec,
                timescale2 = 1, 
                amplitude = 0.5*burst_size, 
                t1 = 5, 
                amplitude3=0.2, 
                t2=12)
    else:
        evolution = star_formation_history(spec=spec)

    return evolution


def create_sf_law(model, conroy_sf=False, spec="insideout"):
    for zone in model.zones:
       zone.Mg0 = 0.

    for i in range(model.n_zones):
        R1 = model.annuli[i]
        R2 = model.annuli[i+1]
        R = (R1 + R2)/2

        if R <= MAX_SF_RADIUS:
            area = np.pi * (R2**2 - R1**2)
            if conroy_sf:
                model.zones[i].tau_star = conroy_sf_law(area)
            elif spec=="twoinfall":
                model.zones[i].tau_star = twoinfall_sf_law(area)
            else:
                model.zones[i].tau_star = vice.toolkit.J21_sf_law(area, mode="sfr")

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


def MH_grad(R):
    R0 = 5
    return 0.29 + (R-R0) * np.where(R<R0, -0.015, -0.090)


class mass_loading:
    def __init__(self, factor=1, tau_s_sf=0):
        self._factor = factor
        self.r = 0.4
        self.tau_s_sf = tau_s_sf
        self.yo = factor * vice.yields.ccsne.settings["o"]
    def __call__(self, R_gal):
        Zo = vice.solar_z("o")*10**MH_grad(R_gal)
        return np.maximum(0,
                -1 + self.r  + self.tau_s_sf
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


