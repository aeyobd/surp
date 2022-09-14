from multizone_sim import run_model
import vice


if __name__ == "__main__":
    vice.yields.ccsne.settings["c"] = 0
    run_model("pure_agb_k16", agb_yields="karakas16", n_yields="J22")
