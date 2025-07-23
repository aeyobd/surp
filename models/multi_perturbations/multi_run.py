import surp
from surp import ViceModel, MWParams
import sys
import argparse
import vice

yield_scale = 1e-10


def ag_run(yield_scale = yield_scale,
           yields_dict = {},
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

    for ele, yield_dict in yields_dict.items():
        vice.yields.agb.settings[ele] = surp.yield_models.ZeroAGB()
        vice.yields.ccsne.settings[ele] = 0
        vice.yields.sneia.settings[ele] = 0

        if "agb" in yield_dict:
            vice.yields.agb.settings[ele] = yield_scale * yield_dict["agb"]
        if "ccsne" in yield_dict:
            vice.yields.ccsne.settings[ele] = yield_scale * yield_dict["ccsne"]
        if "sneia" in yield_dict:
            vice.yields.sneia.settings[ele] = yield_scale * yield_dict["sneia"]

        vice.solar_z[ele] = yield_scale * vice.solar_z("c")


    model = surp.create_model(params)
    model.elements = model.elements + tuple(yields_dict.keys())

    for ele in yields_dict.keys():
        print("element ", ele)
        print("\t agb  : ", vice.yields.agb.settings[ele])
        print("\t ccsne: ", vice.yields.ccsne.settings[ele])
        print("\t sneia: ", vice.yields.sneia.settings[ele])
        print()

    print("created model")
    print(model)
    print(model.zones[80])

    model.run(params.times, overwrite=True, pickle=True)


    #print("ag solar    ", vice.solar_z("ag"))
    #surp.set_yields(yields)
    #vice.solar_z["ag"] = yield_scale * vice.solar_z("c")
    print("ag solar    ", vice.solar_z("ag"))

    print(f"saving processed stars to {model_out} and {stars_out}")
    processed = ViceModel.from_vice(vice_name, params.zone_width, seed=params.seed)
    processed.save(model_out, overwrite=True)
    processed.stars.to_csv(stars_out)
    processed.stars_unsampled.to_csv("stars_all.csv")

    print("bye bye!")
