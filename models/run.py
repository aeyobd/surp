import surp
from surp import ViceModel, MWParams
import sys

if len(sys.argv) < 3:
    print("Usage: python run.py params_file yields_file")
    sys.exit(1)

params_file = sys.argv[1]
yields_file = sys.argv[2]
model_out = "model.json"
stars_out = "stars.csv"
vice_name = "milkyway.vice"


params = surp.MWParams.from_file(params_file)
yields = surp.yields.YieldParams.from_file(yields_file)

print(params)
print(yields)

surp.yields.set_yields(yields)
model = surp.create_model(params)

print("created model")
print(model)
print(model.zones[80])

# model.run(params.times, overwrite=True, pickle=True)


processed = ViceModel.from_vice(vice_name, params.zone_width)
processed.save(model_out, overwrite=True)
processed.stars.to_csv(stars_out)

print("bye bye!")
