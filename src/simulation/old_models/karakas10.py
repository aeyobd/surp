import sys
sys.path.append("..")
from multizone_sim import run_model


if __name__ == "__main__":
    run_model("k10", agb_yields="karakas10", n_yields="J22", dt=0.1)
