import surp
import vice

import sys
sys.path.append("..")
from ag_run import ag_run 


A_0 = 1e-3

agb_model = surp.yield_models.ZeroAGB()
ia_model = 0
cc_model = surp.yield_models.Polynomial_CC([A_0, 3*A_0, 3*A_0, A_0])


if __name__ == "__main__":
    ag_run(
            agb_model = agb_model,
            cc_model = cc_model,
            ia_model = ia_model,
    )
