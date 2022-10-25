import sys
sys.path.append("..")
from multizone_sim import run_model


if __name__ == "__main__":
    run_model("/analytic", agb_yields=yields.y_c_agb(), n_stars=2, migration_mode="diffusion")
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

