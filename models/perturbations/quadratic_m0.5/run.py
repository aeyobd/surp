import surp
import vice

import sys
sys.path.append("..")
from ag_run import ag_run 



agb_model = surp.yield_models.ZeroAGB()
y0 = 0.001
mh0 = -0.5
cc_model = surp.yield_models.Quadratic_CC(y0=y0 * mh0**2, zeta=-2 * y0 * mh0, A=y0, Z1=0.016 * 10**mh0)
ia_model = 0


if __name__ == "__main__":
    ag_run(
            agb_model = agb_model,
            cc_model = cc_model,
            ia_model = ia_model,
    )
