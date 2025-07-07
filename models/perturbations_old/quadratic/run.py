import sys
sys.path.append("..")
from ag_run import ag_run 


import surp
import vice

cc_model = surp.yield_models.Quadratic_CC(y0=0, zeta=0, A=0.001, Z1=surp.Z_SUN*0.1)
agb_model = surp.yield_models.ZeroAGB()
ia_model = 0

if __name__ == "__main__": 
    ag_run(
        agb_model = agb_model,
        cc_model = cc_model,
        ia_model = ia_model,
    )
