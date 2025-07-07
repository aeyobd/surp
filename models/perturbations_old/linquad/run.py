import surp
import vice

import sys
sys.path.append("..")
from ag_run import ag_run 
import math


A_0 = 0.001

cc_model = surp.yield_models.LinQuad_CC(y0=0, zeta=0, A=A_0)

agb_model = surp.yield_models.ZeroAGB()
ia_model = 0


if __name__ == "__main__":
    ag_run(
            agb_model = agb_model,
            cc_model = cc_model,
            ia_model = ia_model,
    )
