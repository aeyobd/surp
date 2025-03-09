import surp
import vice

import sys
sys.path.append("..")
from multi_run import ag_run 

m_h_0 = -1
zeta_0 = 0.001

agb_model = surp.agb_interpolator.interpolator("c")
cc_lin = surp.yield_models.BiLogLin_CC(y0=-m_h_0 * zeta_0, zeta=zeta_0, y1=0)
cc_quad = surp.yield_models.Quadratic_CC(y0=0, zeta=0, A=0.001, Z1=surp.Z_SUN * 10**m_h_0)

yield_scale = 2

yields_dict = {
    "ag" : {
        "agb": yield_scale*agb_model
    },
    "cd" : {
        "ccsne": yield_scale* 0.001
        },
    "in" : {
        "ccsne": yield_scale*cc_lin
    },
    "sn" : {
        "ccsne": yield_scale*cc_quad
    },
}
            

if __name__ == "__main__":
    ag_run(
            yields_dict = yields_dict,
    )
