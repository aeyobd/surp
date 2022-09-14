from multizone_sim import run_model
import vice


if __name__ == "__main__":
    vice.yields.ccsne.settings["c"] = 0
    run_model((__file__)[:-3], agb_yields="ventura13", n_yields="J22", spec="lateburst")
