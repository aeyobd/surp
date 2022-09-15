from multizone_sim import run_model
import vice

if __name__ == "__main__":
    alpha_cc = 1
    alpha_agb = (0.00724 - 0.005*alpha_cc)/0.00111
    vice.yields.ccsne.settings["c"] *= alpha_cc

    run_model((__file__)[:-3], agb_yields="karakas16", agb_factor=alpha_agb, n_yields="J22",
              multithread=True)
