import sys
sys.path.append("..")
from multizone_sim import run_model


if __name__ == "__main__":
    def y_cc(z):
        return 0.0136 * z**0.307
    vice.yields.ccsne.settings["c"] = y_cc
    
    run_model("c11_cc_fit", n_stars=2)
