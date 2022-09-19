from multizone_sim import run_model
import vice

if __name__ == "__main__":

    eta_r = 0.3

    f_agb = 0.4
    y_c = 0.00724 * eta_r
    y_agb = 0.00045
    y_cc = 0.005 * eta_r

    alpha_agb = f_agb*y_c/y_agb
    alpha_cc = (y_c - alpha_agb*y_agb)/y_cc

    print("alpha_agb = %f" % alpha_agb)
    print("alpha_cc = %f" % alpha_cc)

    vice.yields.ccsne.settings["c"] *= alpha_cc * eta_r

    for elem in ["o", "n", "fe"]:
        vice.yields.ccsne.settings[elem] *= eta_r

    run_model((__file__)[:-3], agb_yields="cristallo11", agb_factor=alpha_agb, n_yields="J22", eta_factor=eta_r)
