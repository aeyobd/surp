import surp
from surp import ViceModel, MWParams
import sys
import argparse

# weight function here

def weight_func(mass, metallicity, age):
    return mass * age


args = argparse.ArgumentParser(description="Run a VICE model with the given parameters and yields")

args.add_argument("-i", "--interactive", action="store_true", help="Run the model in interactive (verbose) mode")


args = args.parse_args()

model_out = "model.json"
stars_out = "stars.csv"
vice_name = "../run/milkyway.vice"

params_file = "params.toml"
yields_file = "yield_params.toml"

params = surp.MWParams.from_file(params_file)
yields = surp.yields.YieldParams.from_file(yields_file)

if args.interactive:
    params.verbose = True

print(params)
print(yields)

surp.yields.set_yields(yields)


print(f"saving processed stars to {model_out} and {stars_out}")
processed = ViceModel.from_vice(vice_name, params.zone_width, seed=params.seed, weight_function=weight_func)
processed.save(model_out, overwrite=True)
processed.stars.to_csv(stars_out)
processed.stars_unsampled.to_csv("stars_all.csv")

print("bye bye!")
