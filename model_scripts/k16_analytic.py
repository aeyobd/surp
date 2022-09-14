from multizone_sim import run_model
from surp import yields
import vice


if __name__ == "__main__":
    
    pii = 0.5
    eta_r = 0.4

    for elem in ["n", "o", "fe"]:
        vice.yields.ccsne.settings[elem] *= pii

    def y_c_cc(z):
        return 0.044 * z**0.625

    vice.yields.ccsne.settings["c"] = y_c_cc

    run_model("k16_analytic", agb_yields="karakas16", eta_factor=eta_r, n_yields="J22")
