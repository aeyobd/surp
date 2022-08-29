import sys
sys.path.append("..")
from multizone_sim import run_model


if __name__ == "__main__":
    run_model("karakas10", agb_yields="karakas10")
