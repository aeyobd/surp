import sys
sys.path.append("..")
from ag_run import ag_run 


import surp
import vice


# transition at Z=ZSun, slope of 0.1...
ag_run(
    agb_model = surp.yield_models.ZeroAGB(),
    cc_model = surp.yield_models.BiLogLin_CC(y0=0, zeta=0.001, y1=0),
    ia_model = 0,
)