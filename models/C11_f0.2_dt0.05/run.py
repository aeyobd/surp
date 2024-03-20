import surp
from surp import ViceModel, MWParams

params_file = "params.json"
yields_file = "yield_params.json"
model_out = "model.json"
stars_out = "stars.csv"

params = surp.MWParams.from_file(params_file)
yields = surp.yields.YieldParams.from_file(yields_file)

print(params)
print(yields)

surp.yields.set_yields(yields)
model = surp.create_model(params)

print("created model")

model.run(params.times, overwrite=True, pickle=True)


processed = ViceModel.from_vice(filename, params.zone_width)
processed.save(model_out, overwrite=True)
processed.stars.to_csv(stars_out)

print("bye bye!")
