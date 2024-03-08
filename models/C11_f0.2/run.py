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

model = ViceModel.from_vice("milkyway.vice", params.zone_width)
model.save("model.json", overwrite=True)
model.stars.to_csv("stars.json")

print("bye bye!")
