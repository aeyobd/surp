import sys
sys.path.append("..")
from ag_run import ag_run 


import surp
import vice


ag_run(
    agb_model = surp.yield_models.ZeroAGB(),
    cc_model = 0.001,
    ia_model = 0,
)
