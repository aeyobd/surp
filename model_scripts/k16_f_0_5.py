from multizone_sim import run_model
import vice

if __name__ == "__main__":
    f_agb = 0.5
    y_c = 0.00724
    y_agb = 0.00111
    y_cc = 0.005

    alpha_agb = f_agb*y_c/y_agb
    alpha_cc = (y_c - alpha_agb*y_agb)/y_cc

    print("alpha_agb = %f" % alpha_agb)
    print("alpha_cc = %f" % alpha_cc)

    vice.yields.ccsne.settings["c"] *= alpha_cc

    run_model((__file__)[:-3], agb_yields="karakas16", agb_factor=alpha_agb, n_yields="J22")
