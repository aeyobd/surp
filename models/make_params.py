#!/usr/bin/env python

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
    dirname = make_filename(parser, args)

    if os.path.exists(dirname):
        ans = input(f"overwrite directory {dirname}? (y/N) ")
        if ans != "y":
            print("exiting, directory exists: ", dirname)
            return

    else:
        os.mkdir(dirname)

    yparams, params = make_params(args)

    path = f"./{dirname}/params.json"
    ypath = f"./{dirname}/yield_params.json"
    os.popen(f"cp -f run.py {dirname}")

    print("saving params to ", dirname)
    yparams.save(ypath)
    params.save(path)



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
    parser.add_argument("-c", "--sf_law", default="J21",
                        help="Specifies the sfh law")
    parser.add_argument("-C", "--cc_model", default="BiLogLin",
                        help="Specifies the cc model")
    parser.add_argument("-M", "--migration_mode", default="diffusion", 
                        help="""The migration mode. Default is Diffusion.
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

    parser.add_argument("--alpha_agb", default=None,type=float,
                        help="manually set the AGB scaling factor?")
    parser.add_argument("--m_factor", default=1, type=float,
                        help="mass scaling factor for AGB C",)
    parser.add_argument("-P", "--no_negative", action="store_true",
                        help="no negative agb")
    parser.add_argument("--t_d", default=0.15, type=float,
                        help="min delay time AGB")
    parser.add_argument("--tau_agb", default=0.3, type=float,
                        help="characteristic dtd AGB")
    parser.add_argument("--zeta_agb", default=-0.02, type=float,
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
    parser.add_argument("-j", "--threads", default=1, type=int,
                        help="number of threads to run")
    parser.add_argument("-N", "--agb_n_model", default="A",
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


def make_filename(parser, args):
    if args.output is not None:
        return args.output

    filename = args.agb_model
    filename += arg_to_fname(parser, args, "alpha_agb")
    filename += arg_to_fname(parser, args, "agb_fraction", depends=(args.alpha_agb is None), name="f", always_add=True)
    filename += arg_to_fname(parser, args, "zeta_agb", depends=(args.agb_model == "A"), always_add=True)
    filename += arg_to_fname(parser, args, "t_d", depends=(args.agb_model == "A"), always_add=True)
    filename += arg_to_fname(parser, args, "tau_agb", depends=(args.agb_model == "A"), always_add=True)
    filename += arg_to_fname(parser, args, "m_factor")
    filename += arg_to_fname(parser, args, "no_negative", flag=True)

    filename += arg_to_fname(parser, args, "cc_model", name="")
    filename += arg_to_fname(parser, args, "eta")
    filename += arg_to_fname(parser, args, "zeta")
    filename += arg_to_fname(parser, args, "yl_cc", depends=(args.zl_cc > 0))
    filename += arg_to_fname(parser, args, "zl_cc")

    filename += arg_to_fname(parser, args, "fe_ia_factor", name="fe_ia")
    filename += arg_to_fname(parser, args, "RIa")
    filename += arg_to_fname(parser, args, "agb_n_model", name="N")

    filename += arg_to_fname(parser, args, "spec", name="")
    filename += arg_to_fname(parser, args, "migration_mode", name="")
    filename += arg_to_fname(parser, args, "sigma_R", )
    filename += arg_to_fname(parser, args, "sf_law", name="sfl")
    filename += arg_to_fname(parser, args, "timestep", name="dt")
    filename += arg_to_fname(parser, args, "zone_width", name="w")
    filename += arg_to_fname(parser, args, "n_stars")
    filename += arg_to_fname(parser, args, "threads", name="j")

    return filename



def make_params(args):
    from surp.simulation.parameters import MWParams
    from surp.yield_params import YieldParams
    from make_yields import make_yield_params

    args.agb_model = AGB_KEYS[args.agb_model]
    if args.agb_n_model is not None:
        args.agb_n_model = AGB_KEYS[args.agb_n_model]


    yield_params = make_yield_params(
        agb_model = args.agb_model,
        alpha_agb = args.alpha_agb,
        f_agb = args.agb_fraction,
        zeta_cc = args.zeta, 
        fe_ia_factor = args.fe_ia_factor,
        mass_factor = args.m_factor,
        no_negative = args.no_negative,
        y1 = args.yl_cc,
        Z1 = args.zl_cc,
        agb_n_model = args.agb_n_model,
        t_D = args.t_d,
        tau_agb = args.tau_agb,
        zeta_agb = args.zeta_agb,
        cc_model = args.cc_model,
        yield_scale = args.eta,
    )

    mw_params = MWParams(
        timestep = args.timestep,
        n_stars = args.n_stars,
        migration_mode = args.migration_mode,
        migration = "gaussian",
        sigma_R = args.sigma_R,
        sfh_model = args.spec,
        sf_law = args.sf_law,
        zone_width = args.zone_width,
        RIa = args.RIa,
    )

    return yield_params, mw_params



if __name__ == "__main__":
    main()

