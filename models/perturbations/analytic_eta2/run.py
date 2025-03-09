import surp
import vice

import sys
sys.path.append("..")
from multi_run import ag_run 

m_h_0 = -1
zeta_0 = 0.001

agb_model = surp.yield_models.C_AGB_Model(y0=0.001, zeta=-0.001, tau_agb=1, t_D=0.15)
cc_lin = surp.yield_models.BiLogLin_CC(y0=-m_h_0 * zeta_0, zeta=zeta_0, y1=0)
cc_quad = surp.yield_models.Quadratic_CC(y0=0, zeta=0, A=0.001, Z1=surp.Z_SUN * 10**m_h_0)


yields_dict = {
    "ag" : {
        "agb": agb_model
    },
    "cd" : {
        "ccsne": 0.001
        },
    "in" : {
        "ccsne": cc_lin
    },
    "sn" : {
        "ccsne": cc_quad
    },
    }
            

if __name__ == "__main__":
    ag_run(
            yields_dict = yields_dict,
    )
