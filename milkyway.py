import vice
import numpy as np
from vice.toolkit import hydrodisk

from VICE.migration.src.simulations.migration import diskmigration
from VICE.migration.src.simulations.disks import star_formation_history
import yields
import gc
import os
import sys

# modify yields

MAX_SF_RADIUS = 15.5 #kpc
END_TIME = 13.2

def run_model(name, spec="insideout", n_stars=2, agb_yields="cristallo11", seed=None, multithread=False):
    dt = 0.2 #default 0.01
    zone_width = 0.1
    migration_mode = "diffusion"
    Nstars = min(2*MAX_SF_RADIUS/zone_width * END_TIME/dt * n_stars, 3102519)
    print("Nstars = %i" % Nstars)
    vice.yields.agb.settings["c"] = agb_yields
    
    model = vice.milkyway(zone_width=zone_width,
            name=name,
            n_stars=n_stars,
            verbose=False,
            N= Nstars,
            simple=False
            )

    model.elements = ("fe", "o", "c", "n")
    model.mode = "sfr"
    if multithread:
        model.setup_nthreads = 6
        model.nthreads = 4
    else:
        model.setup_nthreads = 1
        model.nthreads = 1
    model.dt = dt
    model.bins = np.arange(-3, 3, 0.01)
            

    model.migration.stars = diskmigration(model.annuli,
            N = Nstars, mode = migration_mode,
            filename = "%s_analogdata.out" % (name),
            seed = seed)
    model.evolution = star_formation_history(spec = spec,
            zone_width = zone_width)


    model.run(np.arange(0, END_TIME, dt))
    del model
    gc.collect()


if __name__ == "__main__":
    prefix = sys.argv[1]
    name = sys.argv[2]
    run_model(prefix + "/" + name, agb_yields="cristallo11", n_stars=8)

    print("Finished %s" %name)

    # run_model("cristallo11_lateburst", spec="lateburst")
    # run_model("karakas10", agb_yields="karakas10")
    # run_model("karakas10_lateburst", spec="lateburst", agb_yields="karakas10")
    # run_model("ventura13", agb_yields="ventura13")
    # run_model("ventura13_lateburst", agb_yields="ventura13", spec="lateburst")
    # run_model("karakas16", agb_yields="karakas16")
    # run_model("karakas16_lateburst", agb_yields="karakas16", spec="lateburst")
    # run_model("milkyway", seed=0, multithread=False)
    # run_model("milkyway_multithreaded", seed=0)

