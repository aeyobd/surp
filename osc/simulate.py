import sys
import vice

import surp.src.yields
from surp.src.yields import amplified_yields

import surp.src.simulation.multizone_sim
from surp.src.simulation.multizone_sim import run_model
from surp import __version__

y_c_0 = 0.005

zeta_n = 9e-4
y_n_flat = 7.1e-4

Z_Sun = 0.014



def main(prefix, filename, eta=1, beta=0.001, lateburst=False,
         f_agb=0.2, OOB=False, agb_model="C11", A=1.5, 
         fe_ia_factor=1, traditional_f=False, y_c_cc_0=0.0028,
         alpha_n=0.5, dt=0.01, n_stars=2):

    print("Loaded")
    agb_model = {
            "C11": "cristallo11",
            "K10": "karakas10",
            "V13": "ventura13",
            "K16": "karakas16"
            }[agb_model]

    set_yields(eta=eta, beta=beta, fe_ia_factor=fe_ia_factor,
        agb_model=agb_model, oob=OOB, f_agb=f_agb, 
        y_c_cc_0=y_c_cc_0, alpha_n=alpha_n)

    if lateburst:
        spec = "lateburst"
    else:
        spec = "insideout"

    print("configured")

    run_model(filename, prefix=prefix,
              eta_factor=eta, 
              spec=spec, 
              burst_size=A, 
              dt=dt, 
              n_stars=n_stars,
              )
    print("complete")


def set_yields(eta=1, beta=0.001, fe_ia_factor=None,
        agb_model="cristallo11", oob=False, f_agb=0.2,
        alpha_n=0.5, y_c_cc_0=0.0028):


    for elem in ["o", "fe"]:
        vice.yields.ccsne.settings[elem] *= eta
    vice.yields.sneia.settings["fe"] *= eta

    if fe_ia_factor:
        fe_total = vice.yields.sneia.settings["fe"] + vice.yields.ccsne.settings["fe"]
        fe_ia = vice.yields.sneia.settings["fe"] * fe_ia_factor
        fe_cc = fe_total - fe_ia
        vice.yields.ccsne.settings["fe"] = fe_cc
        vice.yields.sneia.settings["fe"] = fe_ia

    alpha_agb, alpha_cc = calc_alpha(agb_model, eta, oob, f_agb)


    for elem in ["o", "c"]:
        if elem == "fe" and agb_model == "ventura13":
            if oob:
                vice.yields.agb.settings[elem] = "cristallo11"
            else:
                vice.yields.agb.settings[elem] = amplified_yields(elem,
                        "cristallo11", alpha_agb)
        else:
            if oob:
                vice.yields.agb.settings[elem] = agb_model
            else:
                vice.yields.agb.settings[elem] = amplified_yields(elem,
                        agb_model, alpha_agb)

    y_cc_n = eta*y_n_flat * (1-alpha_n)
    y_n_0 = eta*y_n_flat * alpha_n

    vice.yields.agb.settings["n"] = lambda M, Z: (zeta_n * (Z/Z_Sun) * M 
                                                  + y_n_0 * M)
    prefactor = y_c_0 * alpha_cc / (y_c_cc_0 + beta)

    def y_c_cc(Z):
        return prefactor * (y_c_cc_0 + beta*(Z/Z_Sun)) 

    vice.yields.ccsne.settings["c"] = y_c_cc

    vice.yields.ccsne.settings["n"] = y_cc_n

    print("Yield settings")

    def print_row(*args):
        for i in range(len(args)):
            arg = args[i]
            if isinstance(arg, float):
                s = "%0.2e" % arg
            else:
                s = str(arg)

            if i==0:
                print(f"{s:8}", end="")
            else:
                print(f"{s:30}", end="")
        print()

    print_row("X", "CC", "agb", "SN Ia")
    for elem in ["c", "n", "o", "fe"]:
        if elem != "c":
            cc = vice.yields.ccsne.settings[elem]
        else:
            cc = f"{prefactor*y_c_cc_0:0.4f} + {beta*prefactor:0.4f}z/z0"

        agb = vice.yields.agb.settings[elem]
        if elem == "n":
            agb = f"({zeta_n:0.4f}*z/z0 + {y_n_0:0.4f})M"
        elif not isinstance(agb, (str, float, int)):
            agb = f"{alpha_agb:0.2f}x{agb_model}"

        sneia = vice.yields.sneia.settings[elem]
        print()
        print_row(elem, cc, agb, sneia)

    print()
    print()



def calc_alpha(agb_model="cristallo11" , eta=1, oob=False, f_agb=0.2):
    # these are derived from multizone runs

    agb_model = agb_model

    y_agbs = {
            "cristallo11": 3.47e-4,
            "karakas10": 5.85e-4,
            "ventura13": 6.0e-5,
            "karakas16": 4.21e-4
    }
    y_agb = y_agbs[agb_model]

    y_c = y_c_0*eta

    if oob:
        alpha_agb = 1
    else:
        alpha_agb = f_agb*y_c/y_agb

    alpha_cc = eta * (1 - f_agb)

    return alpha_agb, alpha_cc
