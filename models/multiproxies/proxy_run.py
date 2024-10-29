import surp
from surp import ViceModel, MWParams
import sys
import argparse
import vice

yield_scale = 1e-6


def set_agb_proxies(element_dict):
    for (element, yield_model) in element_dict.items():
        vice.yields.agb.settings[element] = yield_scale * yield_model
        vice.yields.ccsne.settings[element] = 0
        vice.yields.sneia.settings[element] = 0


def set_cc_proxies(element_dict):
    for (element, yield_model) in element_dict.items():
        vice.yields.agb.settings[element] = surp.yield_models.ZeroAGB()
        vice.yields.ccsne.settings[element] = yield_scale * yield_model
        vice.yields.sneia.settings[element] = 0


def set_ia_proxies(element_dict):
    for (element, yield_model) in element_dict.items():
        vice.yields.agb.settings[element] = surp.yield_models.ZeroAGB()
        vice.yields.ccsne.settings[element] = 0
        vice.yields.sneia.settings[element] = yield_scale * yield_model



def set_solar_z(elements):
    for element in elements:
        vice.solar_z[element] = yield_scale * vice.solar_z("c")

def print_proxies(elements):
    for elem in elements:
        print(f"{elem}:", end=" ")
        print("\tZ:", vice.solar_z[elem], end=" ")
        print(f"\tAGB: {vice.yields.agb.settings[elem]}", end=" ")
        print(f"\tCC: {vice.yields.ccsne.settings[elem]}", end=" ")
        print(f"\tIA: {vice.yields.sneia.settings[elem]}", end=" ")

        print()

def proxy_run(agb_models,
           cc_models,
           ia_models,
    ):
    all_elements = set(agb_models.keys()) | set(cc_models.keys()) | set(ia_models.keys())

    if len(all_elements) < len(agb_models) + len(cc_models) + len(ia_models):
        raise ValueError("Duplicate elements in the yield models")

    

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

    print(yields)
    print(params)

    surp.yields.set_yields(yields)

    set_agb_proxies(agb_models)
    set_cc_proxies(cc_models)
    set_ia_proxies(ia_models)

    set_solar_z(all_elements)
    model = surp.create_model(params)
    model.elements = model.elements + tuple(all_elements)
    print_proxies(all_elements)

    print("created model")
    print(model)
    print(model.zones[80])

    model.run(params.times, overwrite=True, pickle=True)


    print(f"saving processed stars to {model_out} and {stars_out}")
    processed = ViceModel.from_vice(vice_name, params.zone_width)
    processed.save(model_out, overwrite=True)
    processed.stars.to_csv(stars_out)

    print("bye bye!")
