import surp
from surp import ViceModel, MWParams
import sys
import vice
import numpy as np

if len(sys.argv) < 3:
    print("Usage: python run.py params_file yields_file")
    sys.exit(1)

#params_file = sys.argv[1]
#yields_file = sys.argv[2]
model_out = "model.json"
stars_out = "stars.csv"
vice_name = "milkyway.vice"
#

#params = surp.MWParams.from_file(params_file)
#yields = surp.yields.YieldParams.from_file(yields_file)

#print(params)
#print(yields)

zone_width = 0.5
#surp.yields.set_yields(yields)
#model = surp.create_model(params)
model = vice.milkyway(zone_width=zone_width)
model.elements = surp.ELEMENTS

print("created model")
print(model)
i = int(round(len(model.zones) * 0.4))
print(model.zones[i])

# model.run(np.arange(0, 13.2, 0.05), overwrite=True, pickle=True)


processed = ViceModel.from_vice(vice_name, zone_width)
processed.save(model_out, overwrite=True)
processed.stars.to_csv(stars_out)

print("bye bye!")
