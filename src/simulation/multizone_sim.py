import vice
import numpy as np
from vice.toolkit import hydrodisk

import sys
import gc
import os

from .src.simulations.migration import diskmigration
from .src.simulations.disks import star_formation_history

MAX_SF_RADIUS = 15.5 #kpc
END_TIME = 13.2

def run_model(name, prefix=None, migration_mode="diffusion", spec="insideout", n_stars=2, 
              seed=None, multithread=False, dt=0.01, burst_size=1.5, eta_factor=1, 
              ratio_reduce=False):
    """
    This function wraps various settings to make running VICE multizone models
    easier for the carbon paper investigation
    
    Parameters
    ----------
    name: ``str``
        The name of the model
        
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
        see vice.migration.src.simulation.disks.star_formation_history

    n_stars: ``int`` [default: 2]
        The number of stars to create during each timestep of the model.

    multithread: ``bool`` [default: False]
        If true, runs the multithreaded version of the model.
        The maximum number of threads is currently 8
        Requires the development-openmp branch of VICE

    dt: ``float`` [default: 0.01]
        The timestep of the simulation, measured in Gyr.
        Decreasing this value can significantly speed up results

    burst_size: ``float`` [default: 1.5]
        The size of the SFH burst for lateburst model.


    eta_factor: ``float`` [default: 1]
        A factor by which to reduce the model's outflows. 

    ratio_reduce: ``bool``
        
    """

    # collects the first argument of the command as the directory to write
    # the simulation output to
    # this allows OSC to use the temperary directory
    if prefix is None:
        prefix = sys.argv[1]

    zone_width = 0.1
    simple = False
    if migration_mode == "post-process":
        simple = True
        migration_mode = "diffusion"

    Nstars = min(2*MAX_SF_RADIUS/zone_width * END_TIME/dt * n_stars, 3102519)
    print("Nstars = %i" % Nstars)


    
    model = vice.milkyway(zone_width=zone_width,
            name=prefix + name,
            n_stars=n_stars,
            verbose=False,
            N= Nstars,
            simple=simple
            )


    model.elements = ("fe", "o", "mg", "n", "c", "au", "ag")

    model.mode = "sfr"

    model.dt = dt
    model.bins = np.arange(-3, 3, 0.01)
            

    model.migration.stars = diskmigration(model.annuli,
            N = Nstars, mode = migration_mode,
            filename = "%s_analogdata.out" % (prefix + name))
    if spec == "lateburst":
        model.evolution = star_formation_history(spec = spec,
                zone_width = zone_width,
                burst_size = burst_size)
    elif spec == "twoexp":
        model.evolution = star_formation_history(spec = spec,
                zone_width = zone_width, tau=1, amplitude=burst_size, t1=5)
    else:
        model.evolution = star_formation_history(spec = spec,
                zone_width = zone_width)

    # for changing value of eta
    if ratio_reduce:
        def mass_loading(R):
            eta_0 = model.default_mass_loading(R)
            r = 0.4 # this is an approximation
            eta =  (1 - r) * (eta_factor - 1) + eta_factor * eta_0
            if eta < 0:
                eta = 0
            return eta
        model.mass_loading = mass_loading
    else:
        model.mass_loading = lambda R: model.default_mass_loading(R) * eta_factor



    print(model)

    model.run(np.arange(0, END_TIME, dt), overwrite=True, pickle=False)

    print("finished")


