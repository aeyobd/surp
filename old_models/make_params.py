import argparse
import subprocess
import sys
import os
import json

AGB_KEYS = { "C11": "cristallo11",
            "K10": "karakas10",
            "V13": "ventura13",
            "K16": "karakas16",
            "P16": "pignatari16",
            "A": "A"
            }


def main():
    parser, args = parse_args()
    dirname = generate_filename(parser, args)
    params = generate_params(args)

    os.mkdir(dirname)
    path = f"./{dirname}/params.json"

    print("saving params to ", path)
    with open(path, "w") as f:
        f.write(json.dumps(params, indent=4))




def parse_args():
    parser = argparse.ArgumentParser(description="""
         This script makes a directory and generates the config file for the given model""")

    parser.add_argument("-m", "--agb_model", default="C11", 
                        help="the name of the AGB model to use. Can be C11, K10, V13, K16, R18, or A")
    parser.add_argument("-f", "--agb_fraction", type=float, default=0.2, 
                        help="the fraction of AGB C production at solar metallicity")
    parser.add_argument("-z", "--zeta", type=float, default=None, 
                        help="the metallicity dependence of CCSNe C. By default calculated from emperical relationships")


    parser.add_argument("-e", "--eta", type=float, default=1,
                        help="a uniform factor to scale yields by")
    parser.add_argument("-s", "--spec", default="insideout", 
                        help="""star formation specification. Options include
                        [insideout, constant, lateburst, outerburst, 
                        twoexp, threeexp, twoinfall]""")
    parser.add_argument("-c", "--conroy_sf", action="store_true", 
                        help="use the conroy ++ 2022 sfe law")
    parser.add_argument("-M", "--migration_mode", default="gaussian", 
                        help="""The migration mode. Default is Gaussian.
                        Acceptable alternate options include diffusion, post-process, linear, 
                        sudden, and rand_walk""")
    parser.add_argument("-S", "--sigma_R", default=1.27, type=float,
                        help="migration strength in kpc/Gyr^0.5")
    parser.add_argument("-A", "--burst_amplitude", type=float, default=1, 
                        help="the multiplicative amplitude of the late burst")
    parser.add_argument("-i", "--fe_ia_factor", default=1, type=float,
                        help="the iron yield factor of type Ia supernovae ")
    parser.add_argument("-R", "--RIa", default="plaw", 
                        help="SNe Ia DTD")

    parser.add_argument("--alpha_agb", default=None,
                        help="manually set the AGB scaling factor?")
    parser.add_argument("--m_factor", default=1, type=float,
                        help="mass scaling factor for AGB C",)
    parser.add_argument("-P", "--no_negative", action="store_true",
                        help="no negative agb")
    parser.add_argument("--t_d", default=0.15,
                        help="min delay time AGB")
    parser.add_argument("--tau_agb", default=0.3,
                        help="characteristic dtd AGB")
    parser.add_argument("--zeta_agb", default=-0.1,
                        help="metallicity dependence of AGB C in the analytic model")

    parser.add_argument("--yl_cc", default=8.67e-4, type=float,
                        help="the C CC yield at Z=0")
    parser.add_argument("--zl_cc", default=0, type=float,
                        help="Metallicity to switch to low Z CC")

    parser.add_argument("-d", "--timestep", type=float, default=0.02, 
                        help="the size of the simulation time step")
    parser.add_argument("-w", "--zone_width", type=float, default=0.1, 
                        help="the width of the simulation zones")
    parser.add_argument("-n", "--n_stars", type=int, default=1, 
                        help="the number of stars to create at each zone for each timestep")
    parser.add_argument("--filename", default="model",
                        help="the default name of the model filename")
    parser.add_argument("-o", "--output", default=None,
                        help="the directory name to create")
    parser.add_argument("-t", "--test_run", action="store_true", 
                        help="only run a test")
    parser.add_argument("-j", "--threads", default=1, type=int,
                        help="number of threads to run")
    parser.add_argument("-N", "--agb_n_model", default=None,
                        help="the AGB N model to use")
    return parser, parser.parse_args()



def arg_to_fname(parser, args, arg_name, always_add=False, flag=False, name=None, depends=None):
    if depends is not None:
        if not depends:
            return ""

    if name is None:
        name = arg_name

    val = getattr(args, arg_name)
    if not always_add:
        if val == parser.get_default(arg_name):
            return ""

    if flag:
        if val == parser.get_default(arg_name):
            return ""
        else:
            return f"_{name}"

    return f"_{name}{val}"


def generate_filename(parser, args):
    if args.output is not None:
        return args.output

    filename = args.agb_model
    filename += arg_to_fname(parser, args, "zeta_agb", depends=(args.agb_model == "A"), always_add=True)
    filename += arg_to_fname(parser, args, "t_d", depends=(args.agb_model == "A"), always_add=True)
    filename += arg_to_fname(parser, args, "tau_agb", depends=(args.agb_model == "A"), always_add=True)
    filename += arg_to_fname(parser, args, "alpha_agb")
    filename += arg_to_fname(parser, args, "agb_fraction", depends=(args.alpha_agb is None), name="f", always_add=True)
    filename += arg_to_fname(parser, args, "m_factor")
    filename += arg_to_fname(parser, args, "no_negative", flag=True)
    filename += arg_to_fname(parser, args, "eta")
    filename += arg_to_fname(parser, args, "zeta")
    filename += arg_to_fname(parser, args, "yl_cc", depends=(args.zl_cc > 0))
    filename += arg_to_fname(parser, args, "zl_cc")
    filename += arg_to_fname(parser, args, "spec", name="")
    filename += arg_to_fname(parser, args, "migration_mode", name="")
    filename += arg_to_fname(parser, args, "sigma_R", depends = (args.migration_mode in ["gaussian", "rand_walk"]))
    filename += arg_to_fname(parser, args, "fe_ia_factor", name="fe_ia")
    filename += arg_to_fname(parser, args, "RIa")
    filename += arg_to_fname(parser, args, "agb_n_model", name="N")
    filename += arg_to_fname(parser, args, "conroy_sf", flag=True)
    filename += arg_to_fname(parser, args, "timestep", name="dt")
    filename += arg_to_fname(parser, args, "zone_width", name="w")
    filename += arg_to_fname(parser, args, "n_stars")
    filename += arg_to_fname(parser, args, "threads", name="j")

    return filename


def generate_params(args):

    args.agb_model = AGB_KEYS[args.agb_model]
    if args.agb_n_model is not None:
        args.agb_n_model = AGB_KEYS[args.agb_n_model]


    yield_kwargs = dict(
        agb_model = args.agb_model,
        alpha_agb = args.alpha_agb,
        f_agb = args.agb_fraction,
        zeta_cc = args.zeta, 
        fe_ia_factor = args.fe_ia_factor,
        mass_factor = args.m_factor,
        no_negative = args.no_negative,
        yl = args.yl_cc,
        zl = args.zl_cc,
        agb_n_model = args.agb_n_model,
    )

    if args.agb_model == "A":
        yield_kwargs["a_agb_kwargs"] = dict(
            t_D = args.t_d,
            tau_agb = args.tau_agb,
            zeta_agb = args.zeta_agb,
        )

    kwargs = dict(
        eta = args.eta,
        timestep = args.timestep,
        n_stars = args.n_stars,
        migration_mode = args.migration_mode,
        n_threads = args.threads,
        verbose = args.test_run,
        sigma_R = args.sigma_R,
        spec = args.spec,
        lateburst_amplitude = args.burst_amplitude,
        conroy_sf = args.conroy_sf,
        yield_kwargs= yield_kwargs,
        zone_width = args.zone_width,
        RIa = args.RIa,
    )

    return kwargs



if __name__ == "__main__":
    main()

