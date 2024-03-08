import surp
import sys

if len(sys.argv) < 2:
    print("error, argument filename required")


params = surp.MWParams.from_file("params.json")
yields = surp.yields.YieldParams.from_file("yield_params.json")
# params.filename = sys.argv[1]

print(params)
print(yields)

surp.yields.set_yields(yields)
model = surp.create_model(params)

print("created model")

model.run(params.times, overwrite=True, pickle=True)

print("bye!")

