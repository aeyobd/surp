from multizone_sim import run_model
from surp import yields
import vice


if __name__ == "__main__":
    pii = 0.5

    for elem in ["n", "o", "fe"]:
        vice.yields.ccsne.settings[elem] *= pii

    def y_c_cc(z):
        return 0.0146 * z**0.335

    vice.yields.ccsne.settings["c"] = y_c_cc

    run_model("denom", agb_yields="cristallo11", eta_factor=pii, n_yields="J22", ratio_reduce=True)
