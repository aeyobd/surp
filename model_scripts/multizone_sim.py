import vice
import numpy as np
from vice.toolkit import hydrodisk

from VICE.migration.src.simulations.migration import diskmigration
from VICE.migration.src.simulations.disks import star_formation_history
from surp import yields, c_isotopic_yields
from surp.yields import amplified_yields
import gc
import os
import sys

# modify yields

MAX_SF_RADIUS = 15.5 #kpc
END_TIME = 13.2

def run_model(name, migration_mode="diffusion", spec="insideout", n_stars=2, agb_yields="cristallo11", 
              seed=None, multithread=False, dt=0.01, n_yields=None, burst_size=1.5, eta_factor=1, 
              isotopic=False, ratio_reduce=False, agb_factor=1):
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

    agb_yields: ``str`` [default: "cristallo11"]
        The yield set to use for AGB carbon produciton. Acceptable values are
        - "cristallo11"
        - "karakas10"
        - "ventura13"
        - "karakas16"
        Look at VICE for more details

    seed: ``int?`` [default: None]
        The seed to use for the model

    multithread: ``bool`` [default: False]
        If true, runs the multithreaded version of the model.
        The maximum number of threads is currently 8
        Requires the development-openmp branch of VICE

    dt: ``float`` [default: 0.01]
        The timestep of the simulation, measured in Gyr.
        Decreasing this value can significantly speed up results

    n_yields: ``str`` [defalt: None]
        Only acceptable value is "J22", which sets the
        AGB N yields to the analytic form in
        Johnson, et. al. 2022 (Emperical constraints of N)

    burst_size: ``float`` [default: 1.5]
        The size of the SFH burst for lateburst model.


    eta_factor: ``float`` [default: 1]
        A factor by which to reduce the model's outflows. 
        Does not reduce CCSNe yields

    ratio_reduce: ``bool``
        
    """

    # collects the first argument of the command as the directory to write
    # the simulation output to
    # this allows OSC to use the temperary directory
    prefix = sys.argv[1]

    zone_width = 0.1
    simple = False
    if migration_mode == "post-process":
        simple = True
        migration_mode = "diffusion"

    Nstars = min(2*MAX_SF_RADIUS/zone_width * END_TIME/dt * n_stars, 3102519)
    print("Nstars = %i" % Nstars)

    # we use the nitrogen yields in each study
    if type(agb_yields) == str:
        for elem in ["c", "n", "o", "fe"]:
            if elem == "fe" and agb_yields == "ventura13":
                if agb_factor == 1:
                    vice.yields.agb.settings[elem] = "cristallo11"
                else:
                    vice.yields.agb.settings[elem] = amplified_yields(elem, "cristallo11", agb_factor)
            else:
                if agb_factor == 1:
                    vice.yields.agb.settings[elem] = agb_yields
                else:
                    vice.yields.agb.settings[elem] = amplified_yields(elem, agb_yields, agb_factor)

    
    model = vice.milkyway(zone_width=zone_width,
            name=prefix + name,
            n_stars=n_stars,
            verbose=False,
            N= Nstars,
            simple=simple
            )


    # we use au and ag for c12 and c13 respectively
    if isotopic:
        model.elements = ("fe", "o", "n", "au", "ag")
    else:
        model.elements = ("fe", "o", "n", "c")

    model.mode = "sfr"

    # multithreading may or may not work
    if multithread:
        model.setup_nthreads = 8
        model.nthreads = 4
    else:
        model.setup_nthreads = 1
        model.nthreads = 1
    model.dt = dt
    model.bins = np.arange(-3, 3, 0.01)
            

    model.migration.stars = diskmigration(model.annuli,
            N = Nstars, mode = migration_mode,
            filename = "%s_analogdata.out" % (prefix + name),
            seed = seed)
    if spec == "lateburst":
        model.evolution = star_formation_history(spec = spec,
                zone_width = zone_width,
                burst_size = burst_size)
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


    if n_yields == "J22":
        # this is just a coefficient
        xi = 9e-4

        def y_N_agb(m, z):
            return xi* m * (z / 0.014)
        vice.yields.agb.settings["n"] = y_N_agb


    # prints out the input parameters of the model
    print_description(model)

    model.run(np.arange(0, END_TIME, dt), overwrite=True, pickle=False)

    del model
    gc.collect()
    print("finished")


def print_description(model):
    """
    Prints out the element yield settings in the given model
    """
    print(model)
    print("Yield settings")
    for elem in model.elements:
        print(elem)
        print("CCSNE")
        print(vice.yields.ccsne.settings[elem])
        print("AGB")
        print(vice.yields.agb.settings[elem])
        print("SNIa")
        print(vice.yields.sneia.settings[elem])


