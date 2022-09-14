from multizone_sim import run_model
import vice


if __name__ == "__main__":
    #run_model("fiducial", agb_yields="cristallo11", n_stars=8)
    # run_model("fiducial", agb_yields="cristallo11", n_yields="J22")
    def y_cc(z):
        return 0.02 * z**0.25
    
    vice.yields.ccsne.settings["C"] = y_cc
    run_model("inc_agb", n_stars=2, agb_yields = "cristallo11", agb_factor=3, migration_mode="diffusion", n_yields="J22")
