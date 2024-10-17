import sys
sys.path.append("..")
from ag_run import ag_run 


import surp
import vice


# transition at Z=ZSun, slope of 0.1...
zeta_0 = 0.001
m_h_0 = -0.2
ag_run(
    agb_model = surp.yield_models.ZeroAGB(),
    cc_model = surp.yield_models.BiLogLin_CC(y0=-m_h_0 * zeta_0, zeta=zeta_0, y1=0),
    ia_model = 0,
)
