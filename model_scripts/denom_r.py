from multizone_sim import run_model
from surp import yields
import vice


if __name__ == "__main__":
    
    pii = 1/2.5
    eta_r = pii

    for elem in ["n", "o", "fe", "c"]:
        vice.yields.ccsne.settings[elem] *= pii

    run_model("denom_R", agb_yields="cristallo11", eta_factor=eta_r, n_yields="J22", ratio_reduce=True)
