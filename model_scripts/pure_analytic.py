from multizone_sim import run_model
import vice


if __name__ == "__main__":
    def y_cc(z):
        return 0.02 * z**0.25
    vice.yields.ccsne.settings["C"] = y_cc

    def y_agb(m, z):
        return 0
    vice.yields.agb.settings["c"] = y_agb
    
    run_model((__file__)[:-3], n_stars=2, migration_mode="diffusion", n_yields="J22")
