import sys
sys.path.append("..")
from ag_run import ag_run 


import surp
import vice

MH1 = -1.0
Z1 = surp.gce_math.MH_to_Z(MH1)
A = 0.001

b = -MH1 * 2 * A
y0 = MH1**2 * A

cc_model = surp.yield_models.Quadratic_CC(y0=y0, zeta=b, A=A, Z1=Z1)
agb_model = surp.yield_models.ZeroAGB()
ia_model = 0

if __name__ == "__main__": 
    ag_run(
        agb_model = agb_model,
        cc_model = cc_model,
        ia_model = ia_model,
    )
