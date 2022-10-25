from multizone_sim import run_model
import vice
import sys

if __name__ == "__main__":

    # prefix = sys.argv[1]
    f_agb = sys.argv[2]
    beta = sys.argv[3]
    agb_model = sys.argv[4]
    eta = sys.argv[5]

    A = 0.75
    lateburst = False

    name = agb_model + "_f" + f_agb + "_Z" + beta + "_eta" + eta + "_v1"

    if lateburst:
        name += "_lateburst"
    print(name)

    # these are taken from vice singlestellarpopulation runs
    if agb_model == "cristallo11":
        y_agb = 4.04e-4
    elif agb_model == "karakas10":
        y_agb = 6.43e-4
    elif agb_model == "ventura13":
        y_agb = 2.14e-4 # we will see, this model could cause chaos
    elif agb_model == "karakas16":
        y_agb = 4.04e-4
    else:
        raise

    beta = float(beta)
    f_agb = float(f_agb)
    eta = float(eta)

    y_cc_0 = 0.005
    y_c = 0.00724*eta

    alpha_agb = f_agb*y_c/y_agb
    alpha_cc = (y_c - alpha_agb*y_agb)/y_cc_0

    for elem in ["o", "n", "fe"]:
        vice.yields.ccsne.settings[elem] *= eta
    vice.yields.sneia.settings["fe"] *= eta


    def y_cc(z):
        return y_cc_0 * alpha_cc * (z/0.014)**beta

    vice.yields.ccsne.settings["C"] = y_cc

    if lateburst:
        spec = "lateburst"
    else:
        spec = "insideout"

    if A is None:
        pass
        A = 1.5
    else:
        name += "_A%s" % A

    run_model(name, agb_yields=agb_model, agb_factor=alpha_agb, n_yields="J22", eta_factor=eta, spec=spec, burst_size=A)
