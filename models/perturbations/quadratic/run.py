import sys
sys.path.append("..")
from ag_run import ag_run 


import surp
import vice

cc_model = surp.yield_models.Quadratic_CC(y0=0, zeta=0, A=0.001, Z1=0.0016)

ag_run(
    agb_model = surp.yield_models.ZeroAGB(),
    cc_model = cc_model,
    ia_model = 0,
)
