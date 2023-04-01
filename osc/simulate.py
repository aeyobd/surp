import sys
import vice


from surp.src.simulation.multizone_sim import run_model
from surp import __version__
from args import parse_args, find_name

y_c_0 = 0.005
y_c_cc_0 = 0.0029
zeta_n = 7e-4
y_cc_n = 9e-4

Z_Sun = 0.014


def main():
    print("Loaded")
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

    print("configured")

    run_model(name, prefix=prefix, agb_yields=agb_model, agb_factor=alpha_agb,
            n_yields="J22", eta_factor=eta, spec=spec, burst_size=A, dt=0.5)
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

    def y_n_agb(M, Z):
        return 

    vice.yields.agb.settings["N"] = lambda M, Z: zeta_n * (Z/Z_Sun) * M
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

if __name__ == "__main__":
    main()
