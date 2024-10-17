import surp
from surp import ViceModel, MWParams
import sys
import argparse
import vice

yield_scale = 1e-3

def ag_run(yield_scale = 1e-3, 
           agb_model = surp.yield_models.ZeroAGB(),
           cc_model = 0,
           ia_model = 0,
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

    vice.solar_z["ag"] = yield_scale * vice.solar_z("c")

    if args.interactive:
        params.verbose = True

    print(params)
    print(yields)

    surp.yields.set_yields(yields)

    vice.yields.agb.settings["ag"] = yield_scale * agb_model
    vice.yields.ccsne.settings["ag"] =  yield_scale * cc_model
    vice.yields.sneia.settings["ag"] = yield_scale * ia_model

    print("ag: agb     ", vice.yields.agb.settings["ag"])
    print("ag: ccsne   ", vice.yields.ccsne.settings["ag"])
    print("ag: sneia   ", vice.yields.sneia.settings["ag"])
    print("ag solar    ", vice.solar_z["ag"])

    model = surp.create_model(params)
    model.elements = model.elements + ("ag",)

    print("created model")
    print(model)
    print(model.zones[80])

    model.run(params.times, overwrite=True, pickle=True)


    print(f"saving processed stars to {model_out} and {stars_out}")
    processed = ViceModel.from_vice(vice_name, params.zone_width)
    processed.save(model_out, overwrite=True)
    processed.stars.to_csv(stars_out)

    print("bye bye!")
