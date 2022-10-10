from multizone_sim import run_model
import vice
import sys
import argparse


y_cc_0 = 0.005
version = "0.1"


def main():
    args = parse_args()

    f_agb = args.agb_fraction
    beta = args.beta
    agb_model = args.agb_model
    eta = args.eta

    A = args.lateburst_amplitude
    lateburst = args.lateburst

    prefix = args.prefix

    print(args)

    name = find_name(args)


    set_yields(args)

    if lateburst:
        spec = "lateburst"
    else:
        spec = "insideout"

    alpha_agb, alpha_cc = calc_alpha(args)

    run_model(name, prefix=prefix, agb_yields=agb_model, agb_factor=alpha_agb, n_yields="J22", eta_factor=eta, spec=spec, burst_size=A, dt=0.1)


def parse_args():
    parser = argparse.ArgumentParser(description="Runs a multizone model")

    parser.add_argument("prefix")
    parser.add_argument("-e", "--eta", help = "outflow factor", type=float, default=1)
    parser.add_argument("-b", "--beta", help = "C CCSNe Z-dependence", type=float, default=0.3)

    parser.add_argument("-l", "--lateburst", help = "sets sfh to lateburst", action="store_true")
    parser.add_argument("-f", "--agb_fraction", help="The fractional C AGB contribution", type=float, default=0.2)

    parser.add_argument("-m", "--agb_model", help="The AGB yield set to use", type=str, default="cristallo11", 
                        choices=["cristallo11", "karakas10", "ventura13", "karakas16"])

    parser.add_argument("-n", "--filename", help="The name of the file to write the output to")
    parser.add_argument("-A", "--lateburst_amplitude", help="The amplitude of the lateburst", type=int, default=1.5)


    args = parser.parse_args()

    return args


def set_yields(args):
    eta = args.eta

    for elem in ["o", "n", "fe"]:
        vice.yields.ccsne.settings[elem] *= eta
    vice.yields.sneia.settings["fe"] *= eta

    alpha_agb, alpha_cc = calc_alpha(args)

    def y_cc(z):
        return y_cc_0 * alpha_cc * (z/0.014)**args.beta

    vice.yields.ccsne.settings["C"] = y_cc


def find_name(args):
    f_agb = args.agb_fraction
    beta = args.beta
    agb_model = args.agb_model
    eta = args.eta
    A = args.lateburst_amplitude
    lateburst = args.lateburst

    if args.filename:
        name = args.filename
    else:
        name = f"{agb_model}_f{f_agb}_Z{beta}_eta{eta}_v{version}"

        if A == 1.5:
            pass
        else:
            name += "_A%s" % A

        if lateburst:
            name += "_lateburst"

    print(name)
    return name


def calc_alpha(args):
    # these are derived from multizone runs

    agb_model = args.agb_model
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

    y_c = 0.00724*args.eta

    alpha_agb = args.agb_fraction*y_c/y_agb
    alpha_cc = (y_c - alpha_agb*y_agb)/y_cc_0

    return alpha_agb, alpha_cc

if __name__ == "__main__":
    main()
