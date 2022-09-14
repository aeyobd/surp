from multizone_sim import run_model
from surp import yields
import vice


if __name__ == "__main__":
    
    pii = 1
    eta_r = 1

    for elem in ["n", "o", "fe"]:
        vice.yields.ccsne.settings[elem] *= pii

    def y_c_cc(z):
        return 0.033 * z**0.37

    vice.yields.ccsne.settings["c"] = y_c_cc

    run_model("k16_a2", agb_yields="karakas16", eta_factor=eta_r, n_yields="J22")
