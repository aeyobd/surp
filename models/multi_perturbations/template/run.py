import surp
import vice

import sys
sys.path.append("..")
from multi_run import ag_run 

m_h_0 = -1
zeta_0 = 0.001

agb_model = surp.agb_interpolator.interpolator("c")
cc_lin = surp.yield_models.Lin_CC(y0=zeta_0, slope=zeta_0/surp.Z_SUN)
cc_quad = surp.yield_models.LinQuad_CC(y0=zeta_0, slope=zeta_0/surp.Z_SUN, A=zeta_0/surp.Z_SUN**2)


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
