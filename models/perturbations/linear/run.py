import surp
import vice

import sys
sys.path.append("..")
from ag_run import ag_run 



zeta_0 = 0.001
m_h_0 = -2
agb_model = surp.yield_models.ZeroAGB()
cc_model = surp.yield_models.BiLogLin_CC(y0=0, zeta=zeta_0, y1=m_h_0 * zeta_0)
ia_model = 0


if __name__ == "__main__":
    ag_run(
            agb_model = agb_model,
            cc_model = cc_model,
            ia_model = ia_model,
    )
