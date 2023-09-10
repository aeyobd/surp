import argparse
import subprocess
import sys
import os


M_LOW_DEFAULT = 1.3
M_MID_DEFAULT = 2.3
M_HIGH_DEFAULT = 4
N_THREADS_DEFAULT = 1
DT_DEFAULT = 0.02
SIGMA_R_DEFAULT = 1.27
ZETA_AGB_DEFAULT = -0.02


def main():
    args = parse_args()
    filename = args.filename

    for d in ["logs", "out", "results"]:
        os.makedirs(d, exist_ok=True)

    if args.test_run and args.threads is None:
        args.threads = 1
    elif args.threads is None:
        args.threads = N_THREADS_DEFAULT

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
    parser.add_argument("-z", "--zeta", type=float, default=None, 
                        help="the solar fraction of CCSNe secondary C, default=0.7")
    parser.add_argument("-s", "--spec", default="insideout", 
                        help="""star formation specification. Options include
                        [insideout, constant, lateburst, outerburst, 
                        twoexp, threeexp]""")
    parser.add_argument("-f", "--agb_fraction", type=float, default=0.2, 
                        help="the mass fraction of AGB stars in the initial mass function ")
    parser.add_argument("-o", "--out_of_box_agb", action="store_true", 
                        help="use an out-of-box AGB model ")
    parser.add_argument("-c", "--conroy_sf", action="store_true", 
                        help="use the conroy ++ 2022 sfe law")
    parser.add_argument("-m", "--agb_model", default="C11", 
                        help="the name of the AGB model to use ")
    parser.add_argument("-M", "--migration_mode", default="rand_walk", 
                        help="""The migration mode. Default is diffusion.
                        Acceptable options include post-process, linear, 
                        sudden, and rand_walk""")
    parser.add_argument("-S", "--sigma_R", default=SIGMA_R_DEFAULT, type=float,
                        help="migration strength in kpc/Gyr^0.5")
    parser.add_argument("-F", "--filename", default=None,
                        help="the name of the output file ")
    parser.add_argument("-A", "--burst_amplitude", type=float, default=1, 
                        help="the amplitude of the late burst")
    parser.add_argument("-i", "--fe_ia_factor", default="None", 
                        help="the iron yield factor of type Ia supernovae ")
    parser.add_argument("-d", "--timestep", type=float, default=DT_DEFAULT, 
                        help="the size of the time step ")
    parser.add_argument("-n", "--n_stars", type=int, default=1, 
                        help="the number of stars")
    parser.add_argument("-a", "--alpha_n", type=float, default=0, 
                        help="the agb fraction of primary N (0.0)")
    parser.add_argument("-t", "--test_run", action="store_true", 
                        help="only run a test")
    parser.add_argument("-x", "--xi", type=float,
            help="CC Z^2 parameter", default=0)
    parser.add_argument("-j", "--threads", default=None, type=int,
                        help="number of threads to run. default=1")
    parser.add_argument("--m_low", default=M_LOW_DEFAULT,
                        help="lower mass of AGB C")
    parser.add_argument("--m_mid", default=M_MID_DEFAULT,
                        help="lower mass of AGB C")
    parser.add_argument("--m_high", default=M_HIGH_DEFAULT,
                        help="lower mass of AGB C")
    parser.add_argument("--zeta_agb", default=ZETA_AGB_DEFAULT,
                        help="metallicity dependence of agb carbon")
    parser.add_argument("--yl_agb", default=0, 
                        help="agb yield at m0")
    parser.add_argument("--yh_agb", default=0, 
                        help="agb yield at m0")
    parser.add_argument("--m_factor", 
            help="mass factor for agb stars", default=1, type=float)
    parser.add_argument("-P", "--no_negative", 
            help="no negative agb", action="store_true")
    parser.add_argument("--mz_agb", 
            help="mass coupling factor for agb stars", default=0, type=float)
    return parser.parse_args()


def generate_filename(args):
    filename = args.agb_model
    if args.agb_model == "A":
        if (args.m_low != M_LOW_DEFAULT
                or args.m_mid != M_MID_DEFAULT
                or args.m_high != M_HIGH_DEFAULT
                ):
            filename += f"_{args.m_low}_{args.m_mid}_{args.m_high}"

        if args.zeta_agb != ZETA_AGB_DEFAULT:
            filename += f"_z{args.zeta_agb}"
        if args.mz_agb != 0:
            filename += f"_mz{args.mz_agb}"
        if args.yl_agb != 0:
            filename += f"_y0{args.yl_agb}"
        if args.yh_agb != 0:
            filename += f"_y2{args.yh_agb}"

    if args.m_factor != 1:
        filename += f"_m{args.m_factor}"
    if args.no_negative:
        filename += "_P"

    if args.out_of_box_agb:
        filename += "_oob"
    else:
        filename += "_f" + str(args.agb_fraction)

    if args.eta != 1:
        filename += "_eta" + str(args.eta) 
        
    if args.zeta is not None:
        filename += "_zeta" + str(args.zeta)

    if args.xi != 0:
        filename += "_xi" + str(args.xi)

    if args.spec != "insideout":
        filename += "_" + args.spec + str(args.burst_amplitude)

    if args.migration_mode != "rand_walk":
        filename += "_" + args.migration_mode
    if args.migration_mode == "rand_walk" and args.sigma_R != SIGMA_R_DEFAULT:
        filename += str(args.sigma_R)

    if args.fe_ia_factor != "None":
        filename += "_Fe" + str(args.fe_ia_factor)

    if args.conroy_sf:
        filename += "_c22"

    if args.timestep != DT_DEFAULT:
        filename += "_dt" + str(args.timestep)

    if args.alpha_n != 0:
        filename += "_an" + str(args.alpha_n)

    if args.n_stars != 1:
        filename += "_nstars" + str(args.n_stars)

    if args.threads != N_THREADS_DEFAULT:
        filename += "_j" + str(args.threads)

    return filename


def create_pycall(filename, args):
    # create call to python script
    pycall = f"""\
path = None
import surp.simulation.filter_warnings
from surp.simulation.multizone_sim import run_model


yield_kwargs = {{
     'oob': {args.out_of_box_agb},
     'f_agb': {args.agb_fraction},
     'zeta': {args.zeta}, 
     'fe_ia_factor': {args.fe_ia_factor},
     'm_low': {args.m_low},
     'm_mid': {args.m_mid},
     'm_high': {args.m_high},
     'zeta_agb': {args.zeta_agb},
     'yl_agb': {args.yl_agb},
     'yh_agb': {args.yh_agb},
     'alpha_n': {args.alpha_n},
     'mass_factor': {args.m_factor},
     'mz_agb': {args.mz_agb},
     'no_negative': {args.no_negative},
     'xi': {args.xi},
}}

kwargs = {{
     'n_stars': {args.n_stars},
     'migration_mode': '{args.migration_mode}',
     'n_threads': {args.threads},
     'verbose': {args.test_run},
     'sigma_R': {args.sigma_R},
     'spec': '{args.spec}',
     'lateburst_amplitude': {args.burst_amplitude},
     'conroy_sf': {args.conroy_sf},
}}

run_model('{filename}',
     save_dir=path,
     agb_model='{args.agb_model}',
     eta={args.eta}, 
     timestep={args.timestep},
     yield_kwargs=yield_kwargs,
     **kwargs
    )
"""
    return pycall




if __name__ == "__main__":
    main()




