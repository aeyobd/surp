from multizone_sim import run_model
import vice


if __name__ == "__main__":
    #run_model("fiducial", agb_yields="cristallo11", n_stars=8)
    # run_model("fiducial", agb_yields="cristallo11", n_yields="J22")
    def y_cc(z):
        return 0.60 * z**1.06
    vice.yields.ccsne.settings["C"] = y_cc
    
    run_model((__file__)[:-3], n_stars=2, agb_yields = "ventura13", migration_mode="diffusion", agb_factor=3, n_yields="J22")