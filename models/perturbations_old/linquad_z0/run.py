import surp
import numpy as np
import vice

import sys
sys.path.append("..")
from ag_run import ag_run 
import math


A_0 = 0.001 / surp.Z_SUN**2

slope = +2 * A_0  * surp.Z_SUN
zeta = slope * surp.Z_SUN * np.log(10) 
y0 = surp.Z_SUN**2 * A_0

cc_model = surp.yield_models.LinQuad_CC(y0=y0, zeta=zeta, A=A_0)

agb_model = surp.yield_models.ZeroAGB()
ia_model = 0


if __name__ == "__main__":
    ag_run(
            agb_model = agb_model,
            cc_model = cc_model,
            ia_model = ia_model,
    )
