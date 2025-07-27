import surp
import vice

import sys
sys.path.append("..")
from ag_run import ag_run 



agb_model = surp.yield_models.ZeroAGB()
ia_model = 0

A_0 = 0.001
cc_model = surp.yield_models.LinQuad_CC(y0=A_0, slope=2*A_0/surp.Z_SUN, A=A_0 / surp.Z_SUN**2)


if __name__ == "__main__":
    ag_run(
            agb_model = agb_model,
            cc_model = cc_model,
            ia_model = ia_model,
    )
