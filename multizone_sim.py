import vice
import numpy as np
from vice.toolkit import hydrodisk

from VICE.migration.src.simulations.migration import diskmigration
from VICE.migration.src.simulations.disks import star_formation_history
from surp import yields, c_isotopic_yields
import gc
import os
import sys

# modify yields

MAX_SF_RADIUS = 15.5 #kpc
END_TIME = 13.2

def run_model(name, migration_mode="diffusion", spec="insideout", n_stars=2, agb_yields="cristallo11", 
              seed=None, multithread=False, dt=0.01, n_yields=None, burst_size=1.5, eta_factor=1, reduced_n=True, isotopic=True):
    """
    This function wraps various settings to make running VICE multizone models
    easier for the carbon paper investigation
    
    Parameters
    ----------
    name: str
        The name of the model
        
    migration_mode: str
        Default value: diffusion
        The migration mode for the simulation. 
        Can be one of diffusion (most physical), linear, post-process, ???
        
        
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
                vice.yields.agb.settings[elem] = "cristallo11"
            else:
                vice.yields.agb.settings[elem] = agb_yields

    
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
    model.mass_loading = lambda R: model.default_mass_loading(R) * eta_factor

    # non reduced_n makes model consistant with J+22
    # we are not using this anymore as it is unphysical
    # if reduced_n:
    #     elems = ["n", "o", "fe"]
    # else:
    #     elems = ["o", "fe"]

    # for ele in model.elements:
    #     val = vice.yields.ccsne.settings[ele]
    #     if type(val) is float:
    #         vice.yields.ccsne.settings[ele] *= eta_factor
    #     else:
    #         vice.yields.ccsne.settings[ele] = lambda z: eta_factor*vice.yields.ccsne.settings[ele](z)
        # vice.yields.sneia.settings[ele] *= eta_factor

        # vice.yields.agb.settings[ele] = yields.amplified_yields(ele, prefactor=eta_factor)

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

