import surp
import vice

import sys
sys.path.append("..")
from ag_run import ag_run 

Zs = [0.000176, 0.00176, 0.00442092, 0.00700669, 
      0.01110485, 0.0176, 0.02789412, 0.0442092]

A = 1e-3
ys = [0, A, 0, 0,
      0, 0, 0, 0]

agb_model = surp.yield_models.ZeroAGB()
cc_model = surp.yield_models.Spline_CC(Zs, ys)
ia_model = 0


if __name__ == "__main__":
    ag_run(
            agb_model = agb_model,
            cc_model = cc_model,
            ia_model = ia_model,
    )
