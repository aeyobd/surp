import surp
from surp import ViceModel, MWParams

params_file = "params.json"
yields_file = "yield_params.json"

params = surp.MWParams.from_file(params_file)
yields = surp.yields.YieldParams.from_file(yields_file)

print(params)
print(yields)

surp.yields.set_yields(yields)
model = surp.create_model(params)

print("created model")

model.run(params.times, overwrite=True, pickle=True)


model = load_model(filename, params.zone_width)
model.save(json_name, overwrite=True)
save_stars(model, args.stars)
model.stars.to_csv(filename)

print("bye bye!")
