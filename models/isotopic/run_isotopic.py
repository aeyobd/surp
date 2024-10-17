import surp
from surp import ViceModel, MWParams
import sys
import argparse
import vice

# TODO determine solar isotopic ratio

def run_isotopic(
        agb_c12 = 0,
        agb_c13 = 0,
        cc_c12 = 0,
        cc_c13 = 0,
        sneia_c12 = 0,
        sneia_c13 = 0,
    ):

    # everything below is mostly unchanged
    args = argparse.ArgumentParser(description="Run a VICE model with the given parameters and yields")

    args.add_argument("params_file", type=str, help="The file containing the parameters for the model")

    args.add_argument("yields_file", type=str, help="The file containing the yields for the model")

    args.add_argument("-i", "--interactive", action="store_true", help="Run the model in interactive (verbose) mode")


    args = args.parse_args()

    params_file = args.params_file
    yields_file = args.yields_file
    model_out = "model.json"
    stars_out = "stars.csv"
    vice_name = "milkyway.vice"


    params = surp.MWParams.from_file(params_file)
    yields = surp.yields.YieldParams.from_file(yields_file)


    if args.interactive:
        params.verbose = True

    print(params)
    print(yields)

    surp.yields.set_yields(yields)
    surp.yields.set_mag22_scale(isotopic=True, verbose=True)

    vice.yields.agb.settings["hg"] = agb_c12
    vice.yields.ccsne.settings["hg"] =  cc_c12
    vice.yields.sneia.settings["hg"] = sneia_c12
    
    vice.yields.agb.settings["tl"] = agb_c13
    vice.yields.ccsne.settings["tl"] =  cc_c13
    vice.yields.sneia.settings["tl"] = sneia_c13

    print("c12")
    print("agb     ", vice.yields.agb.settings["hg"])
    print("ccsne   ", vice.yields.ccsne.settings["hg"])
    print("sneia   ", vice.yields.sneia.settings["hg"])

    print("c13")
    print("agb     ", vice.yields.agb.settings["tl"])
    print("ccsne   ", vice.yields.ccsne.settings["tl"])
    print("sneia   ", vice.yields.sneia.settings["tl"])

    model = surp.create_model(params)
    model.elements = ("fe", "o", "au", "ag")

    print("created model")
    print(model)
    print(model.zones[80])

    model.run(params.times, overwrite=True, pickle=True)


    print(f"saving processed stars to {model_out} and {stars_out}")
    processed = ViceModel.from_vice(vice_name, params.zone_width)
    processed.save(model_out, overwrite=True)
    processed.stars.to_csv(stars_out)

    print("bye bye!")
