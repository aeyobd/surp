import sys
import vice

import argparse

from surp.src.simulation.multizone_sim import run_model
from surp import __version__

y_c_0 = 0.005
y_c_cc_0 = 0.0029
zeta_n = 9e-4
y_cc_n = 3.6e-4
y_n_0 = 3.6e-4

Z_Sun = 0.014


def main():
    print("Loaded")
    args = parse_args()
    f_agb = args.agb_fraction
    beta = args.beta
    eta = args.eta

    args.agb_model = {
            "C11": "cristallo11",
            "K10": "karakas10",
            "V13": "ventura13",
            "K16": "karakas16"
            }[args.agb_model]

    A = args.lateburst_amplitude
    lateburst = args.lateburst

    prefix = args.prefix

    print(args)

    name = args.filename

    set_yields(args)

    if lateburst:
        spec = "lateburst"
    else:
        spec = "insideout"

    alpha_agb, alpha_cc = calc_alpha(args)

    print("configured")

    run_model(name, prefix=prefix, agb_yields=args.agb_model, agb_factor=alpha_agb,
            eta_factor=eta, spec=spec, burst_size=A)
    print("complete")


def set_yields(args):
    eta = args.eta
    vice.yields.ccsne.settings["N"] = y_cc_n

    for elem in ["o", "n", "fe"]:
        vice.yields.ccsne.settings[elem] *= eta
    vice.yields.sneia.settings["fe"] *= eta

    if args.fe_ia_factor:
        fe_total = vice.yields.sneia.settings["fe"] + vice.yields.ccsne.settings["fe"]
        fe_ia = vice.yields.sneia.settings["fe"] * args.fe_ia_factor
        fe_cc = fe_total - fe_ia
        vice.yields.ccsne.settings["fe"] = fe_cc
        vice.yields.sneia.settings["fe"] = fe_ia

    alpha_agb, alpha_cc = calc_alpha(args)


    def y_c_cc(Z):
        prefactor = y_c_0 * alpha_cc / (y_c_cc_0 + args.beta)

        return prefactor * (y_c_cc_0 + args.beta*(Z/Z_Sun)) 

    vice.yields.agb.settings["N"] = lambda M, Z: (zeta_n * (Z/Z_Sun) * M 
                                                  + y_n_0 * M)
    vice.yields.ccsne.settings["C"] = y_c_cc



def calc_alpha(args):
    # these are derived from multizone runs

    agb_model = args.agb_model

    y_agbs = {
            "cristallo11": 3.47e-4,
            "karakas10": 5.85e-4,
            "ventura13": 6.0e-5,
            "karakas16": 4.21e-4
    }
    y_agb = y_agbs[agb_model]

    y_c = 0.005*args.eta

    oob = args.out_of_box_agb

    if oob:
        alpha_agb = 1
    else:
        alpha_agb = args.agb_fraction*y_c/y_agb

    alpha_cc = (y_c - alpha_agb*y_agb)/y_c

    return alpha_agb, alpha_cc

def parse_args():
    parser = argparse.ArgumentParser(description="Runs a multizone model")

    parser.add_argument("prefix", help = "directory where to put outputs/ in ")
    parser.add_argument("filename", help = "name of the file")
    parser.add_argument("-e", "--eta", help = "outflow factor", type=float, default=1)
    parser.add_argument("-b", "--beta", help = "C CCSNe Z-dependence",
            type=float, default=0.001)

    parser.add_argument("-l", "--lateburst", help = "sets sfh to lateburst", action="store_true")
    parser.add_argument("-f", "--agb_fraction", help="The fractional C AGB contribution", type=float, default=0.2)

    parser.add_argument("-o", "--out_of_box_agb", help="Use the published (unamplified) agb table yields. Overrides -f option", action="store_true")

    parser.add_argument("-m", "--agb_model", help="The AGB yield set to use",
            type=str, default="C11", 
                        choices=["C11", "K10", "V13", "K16"])

    parser.add_argument("-A", "--lateburst_amplitude", help="The amplitude of the lateburst", type=float, default=1.5)

    parser.add_argument("-i", "--fe_ia_factor", help="The factor by which to chante SneIa Fe contribution", type=float)

    parser.add_argument("-t", "--traditional_f", help="Sets the AGB fraction to only imf averaged as is typical defined", action="store_false")

    args = parser.parse_args()

    return args



if __name__ == "__main__":
    main()
