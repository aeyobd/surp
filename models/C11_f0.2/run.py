import surp


params = surp.MWParams.from_file("params.json")
yields = surp.yields.YieldParams.from_file("yield_params.json")

print(params)
print(yields)

surp.yields.set_yields(yields)
model = surp.create_model(params)

model.verbose = True
print("created model")

model.run(params.times, overwrite=True, pickle=True)

print("bye!")

