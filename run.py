import argparse
import subprocess
import sys
import os


def main():
    args = parse_args()
    filename = args.filename

    for d in ["logs", "out", "results"]:
        os.makedirs(d, exist_ok=True)

    if not filename:
        filename = generate_filename(args)

    print(filename)

    pycall = create_pycall(filename, args)
    print(pycall)

    if args.test_run:
        subprocess.call(["bash", "local_run.sh", filename, pycall,
            str(args.threads)])
    else:
        subprocess.call(["bash", "submit.sh", filename, pycall,
            str(args.threads)])



def parse_args():
    parser = argparse.ArgumentParser(description="Argument parser")

    parser.add_argument("-e", "--eta", type=float, default=1,
                        help="the efficiency multiplier of the supernova feedback")
    parser.add_argument("-b", "--beta", type=float, default=0.001, 
                        help="the power-law index of the star formation law, default=0.001")
    parser.add_argument("-s", "--spec", default="insideout", 
                        help="""star formation specification. Options include
                        [insideout, constant, lateburst, outerburst, 
                        twoexp, threeexp]""")
    parser.add_argument("-f", "--agb_fraction", type=float, default=0.2, 
                        help="the mass fraction of AGB stars in the initial mass function ")
    parser.add_argument("-o", "--out_of_box_agb", action="store_true", 
                        help="use an out-of-box AGB model ")
    parser.add_argument("-m", "--agb_model", default="C11", 
                        help="the name of the AGB model to use ")
    parser.add_argument("-M", "--migration_mode", default="diffusion", 
                        help="""The migration mode. Default is diffusion.
                        Acceptable options include post-process, linear, 
                        sudden, and gaussian""")
    parser.add_argument("-F", "--filename", default=None,
                        help="the name of the output file ")
    parser.add_argument("-A", "--lateburst_amplitude", type=float, default=1.5, 
                        help="the amplitude of the late burst")
    parser.add_argument("-i", "--fe_ia_factor", default="None", 
                        help="the iron yield factor of type Ia supernovae ")
    parser.add_argument("-d", "--timestep", type=float, default=0.01, 
                        help="the size of the time step ")
    parser.add_argument("-n", "--n_stars", type=int, default=2, 
                        help="the number of stars")
    parser.add_argument("-a", "--alpha_n", type=float, default=0, 
                        help="the agb fraction of primary N (0.0)")
    parser.add_argument("-t", "--test_run", action="store_true", 
                        help="only run a test")
    parser.add_argument("-T", "--threads", default=8,
                        help="number of threads to run. default=1")
    parser.add_argument("--m_low", default=1.3,
                        help="lower mass of AGB C")
    parser.add_argument("--m_mid", default=2.3,
                        help="lower mass of AGB C")
    parser.add_argument("--m_high", default=4.3,
                        help="lower mass of AGB C")
    parser.add_argument("--mz_agb", default=7e-4,
                        help="metallicity dependence of agb carbon")
    return parser.parse_args()


def generate_filename(args):
    filename = args.agb_model
    if args.agb_model == "A":
        filename += f"_{args.m_low}_{args.m_mid}_{args.m_high}_z{args.mz_agb}"

    if args.out_of_box_agb:
        filename += "_oob"
    else:
        filename += "_f" + str(args.agb_fraction)

    filename += "_eta" + str(args.eta) + "_beta" + str(args.beta)

    if args.spec != "insideout":
        filename += "_" + args.spec + str(args.lateburst_amplitude)
    if args.migration_mode != "diffusion":
        filename += "_" + args.migration_mode

    if args.fe_ia_factor != "None":
        filename += "_Fe" + str(args.fe_ia_factor)

    if args.timestep != 0.01:
        filename += "_dt" + str(args.timestep)

    if args.alpha_n != 0:
        filename += "_an" + str(args.alpha_n)

    if args.n_stars != 2:
        filename += "_nstars" + str(args.n_stars)

    if args.threads != 8:
        filename += "_nthreads" + str(args.threads)

    return filename


def create_pycall(filename, args):
    # create call to python script
    pycall = f"""\
path = None
from surp.simulation.multizone_sim import run_model

run_model(
     filename='{filename}',
     prefix=path,
     eta={args.eta}, 
     beta={args.beta}, 
     spec='{args.spec}',
     agb_fraction={args.agb_fraction},
     out_of_box_agb={args.out_of_box_agb},
     agb_model='{args.agb_model}',
     lateburst_amplitude={args.lateburst_amplitude},
     fe_ia_factor={args.fe_ia_factor},
     timestep={args.timestep},
     n_stars={args.n_stars},
     alpha_n={args.alpha_n},
     migration_mode='{args.migration_mode}',
     n_threads={args.threads},
     m_low={args.m_low},
     m_mid={args.m_mid},
     m_high={args.m_high},
     mz_agb={args.mz_agb},
    )
"""
    return pycall




if __name__ == "__main__":
    main()




