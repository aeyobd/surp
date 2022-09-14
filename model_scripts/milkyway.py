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


    if isotopic:
        model.elements = ("fe", "o", "n", "au", "ag")
    else:
        model.elements = ("fe", "o", "n", "c")

    model.mode = "sfr"
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
    if reduced_n:
        elems = ["n", "o", "fe"]
    else:
        elems = ["o", "fe"]

    for ele in elems:
        vice.yields.ccsne.settings[ele] *= eta_factor
        # vice.yields.sneia.settings[ele] *= eta_factor

        # vice.yields.agb.settings[ele] = yields.amplified_yields(ele, prefactor=eta_factor)

    if n_yields == "J22":
        xi = 9e-4
        def y_N_agb(m, z):
            return 9e-4* m * (z / 0.014)
        vice.yields.agb.settings["n"] = y_N_agb


    print_description(model)

    model.run(np.arange(0, END_TIME, dt), overwrite=True, pickle=False)
    del model
    gc.collect()
    print("finished")


def print_description(model):
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



if __name__ == "__main__":
    # run_model("/analytic", agb_yields=yields.y_c_agb(), n_stars=2, migration_mode="diffusion")
    # run_model("/analytic_post_process", agb_yields=yields.y_c_agb(), n_stars=2, migration_mode="post-process")
    # vice.yields.ccsne.settings["c"] *= 2.5
    # run_model("/cristallo11_amplified", agb_yields=yields.amplified_yields("c", prefactor=2.5))


    # run_model("cristallo11", agb_yields="cristallo11")
    # run_model("karakas10", agb_yields="karakas10")
    # run_model("ventura13", agb_yields="ventura13")
    # run_model("karakas16", agb_yields="karakas16")

    # lateburst models
    # run_model("cristallo11_lateburst", spec="lateburst", dt=0.05)
    # run_model("ventura13_lateburst", agb_yields="ventura13", spec="lateburst", dt=0.05)
    # run_model("karakas10_lateburst", spec="lateburst", agb_yields="karakas10", dt=0.05)
    # run_model("karakas16_lateburst", agb_yields="karakas16", spec="lateburst", dt=0.05)

    # constant sfh models
    #run_model("cristallo11_static", spec="static", dt=0.05)
    #run_model("ventura13_static", agb_yields="ventura13", spec="static", dt=0.05)
    #run_model("karakas10_static", spec="static", agb_yields="karakas10", dt=0.05)
    #run_model("karakas16_static", agb_yields="karakas16", spec="static", dt=0.05)

    # linear n yields
    # run_model("cristallo11_J22", n_yields="J22")

    # increased burst size
    # run_model("cristallo11_lateburst_2", burst_size = 2, spec="lateburst")
    # run_model("cristallo11_lateburst_1", burst_size = 1, spec="lateburst")

    # decresead eta
    # run_model("cristallo11_reduced_eta", eta_factor=1/3)
    # run_model("cristallo11_reduced_eta_n", eta_factor=1/3, reduced_n=False)

    # run_model("cristallo11_8_stars_1", n_stars=8, seed=1)
    # run_model("cristallo11_1", seed=1)
    # run_model("cristallo11_multithreaded_1", seed=1, multithread=True)

    # from vice.yields.ccsne import LC18
    # LC18.set_params(rotation = 300)
    # run_model("cristallo11_lc18", agb_yields="cristallo11")

    # M_Hs = [-3, -2, -1, 0]
    # y_c = [vice.yields.ccsne.fractional("c", MoverH=M_H, rotation=300, study="LC18")[0] for M_H in M_Hs]
    # y_n = [vice.yields.ccsne.fractional("n", MoverH=M_H, rotation=300, study="LC18")[0] for M_H in M_Hs]
    # Z = [0.014*10**M_H for M_H in M_Hs]
    # f = vice.toolkit.interpolation.interp_scheme_1d(Z, y_c)
    # f_n = vice.toolkit.interpolation.interp_scheme_1d(Z, y_n)
    # vice.yields.ccsne.settings["C"] = f
    # vice.yields.ccsne.settings["N"] = f_n

    # run_model("cristallo11_lc18z", agb_yields="cristallo11")
    

    # M_Hs = [-3, -2, -1, 0]
    # y_c = [vice.yields.ccsne.fractional("c", MoverH=M_H, rotation=150, study="LC18")[0] for M_H in M_Hs]
    # y_n = [vice.yields.ccsne.fractional("n", MoverH=M_H, rotation=150, study="LC18")[0] for M_H in M_Hs]
    # Z = [0.014*10**M_H for M_H in M_Hs]
    # f = vice.toolkit.interpolation.interp_scheme_1d(Z, y_c)
    # f_n = vice.toolkit.interpolation.interp_scheme_1d(Z, y_n)
    # vice.yields.ccsne.settings["C"] = f
    # vice.yields.ccsne.settings["N"] = f_n

    # run_model("cristallo11_lc18_150z", agb_yields="cristallo11", reduced_n=False)

    # run_model("cristallo11_reduced_eta_J22", agb_yields="cristallo11", eta_factor=1/3, n_yields="J22")

    # moderate model...
    # fraction = 0.2
    # M_Hs = [-3, -2, -1, 0]
    # y_c = [(1-fraction) * 0.002 + fraction*vice.yields.ccsne.fractional("c", MoverH=M_H, rotation=300, study="LC18")[0] for M_H in M_Hs]
    # y_n = [(1-fraction) * 3.6e-4 + fraction*vice.yields.ccsne.fractional("n", MoverH=M_H, rotation=300, study="LC18")[0] for M_H in M_Hs]
    # Z = [0.014*10**M_H for M_H in M_Hs]
    # f = vice.toolkit.interpolation.interp_scheme_1d(Z, y_c)
    # f_n = vice.toolkit.interpolation.interp_scheme_1d(Z, y_n)
    # vice.yields.ccsne.settings["C"] = f
    # vice.yields.ccsne.settings["N"] = f_n
    # run_model("cristallo11_partial_lc18_reduced_eta", agb_yields="cristallo11", reduced_n=False, eta_factor=1/2)

    # analytic model
    # def y_cc(z):
    #     return 0.0136 * z**0.307
    # vice.yields.ccsne.settings["C"] = y_cc
    
    # run_model("c11_cc_fit", n_stars=2, migration_mode="diffusion", n_yields="J22", eta_factor=0.5)
    run_model("c11_isotopic_lateburst", n_stars=1, dt=0.01, migration_mode="diffusion", spec="lateburst" )

