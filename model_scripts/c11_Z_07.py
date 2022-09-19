from multizone_sim import run_model
import vice

if __name__ == "__main__":

    alpha_agb = 6

    def y_cc(z):
        return 0.005 * (z/0.014)**0.7

    vice.yields.ccsne.settings["C"] = y_cc

    run_model((__file__)[:-3], agb_yields="cristallo11", agb_factor=alpha_agb, n_yields="J22")
