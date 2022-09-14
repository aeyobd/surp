from multizone_sim import run_model
import vice


if __name__ == "__main__":
    def y_cc(z):
        return 2.82 * z**1.55
    vice.yields.ccsne.settings["C"] = y_cc
    
    run_model((__file__)[:-3], n_stars=2, agb_yields="karakas10", migration_mode="diffusion", agb_factor=3, n_yields="J22")
