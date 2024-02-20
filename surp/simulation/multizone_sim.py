import numpy as np

import vice
from vice.milkyway.milkyway import _get_radial_bins

from vice.toolkit.rand_walk.rand_walk_stars import rand_walk_stars 
from vice.toolkit.gaussian.gaussian_stars import gaussian_stars 

from .star_formation_history import create_evolution, create_sf_law
from ..yields import set_yields
from .._globals import MAX_SF_RADIUS, END_TIME, N_MAX


def run_model(filename,
              eta=1,
              agb_model="C11",
              timestep=0.01,
              yield_kwargs={},
              **kwargs
     ):
    """
    creates and runs a vice model. See also create_model for the full parameter choices
    """
    print("initialized")

    set_yields(yield_scale=eta, **yield_kwargs)

    print("configured yields")

    model = create_model(filename, timestep=timestep, eta=eta, **kwargs)

    print(model)

    model.run(np.arange(0, END_TIME, timestep), overwrite=True, pickle=True)

    print("finished")



def create_model(filename, timestep=0.02,
        n_stars=2, 
        spec="insideout",
        eta=1, 
        migration_mode="gaussian", 
        lateburst_amplitude=1,
        n_threads=1, 
        sigma_R=1.27, 
        verbose=False,
        conroy_sf=False, 
        RIa="plaw",
        zone_width=0.01):

    """"
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

    if migration_mode == "post-process":
        simple = True
        migration_mode = "diffusion"
    else:
        simple = False


    Nstars = 2*MAX_SF_RADIUS/zone_width * END_TIME/timestep * n_stars
    if migration_mode != "rand_walk" and Nstars > N_MAX:
        Nstars = N_MAX

    print("using %i stars particles" % Nstars)


    model = vice.milkyway(zone_width=zone_width,
            name = filename,
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
    model.RIa = RIa
    print("sneia model: ", RIa)
    print("using setup threads = ", n_threads)
    print("using model threads = ", model.nthreads)
            
    model.evolution = create_evolution(spec=spec, burst_size=lateburst_amplitude, zone_width=zone_width)

    create_sf_law(model, conroy_sf=conroy_sf, spec=spec)

    if migration_mode == "rand_walk":
        model.migration.stars = rand_walk_stars(
                _get_radial_bins(zone_width),
                n_stars=n_stars, 
                dt=timestep, 
                name=model.name, 
                sigma_R=sigma_R)
    elif migration_mode == "gaussian":
        model.migration.stars = gaussian_stars(
                _get_radial_bins(zone_width),
                n_stars=n_stars, 
                dt=timestep, 
                name=model.name, 
                sigma_R=sigma_R)


    model.mass_loading = mass_loading()

    return model




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

