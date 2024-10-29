import sys
sys.path.append("..")
from proxy_run import proxy_run 

import surp
import vice


y0 = 0.001
agb_proxies = {
    "ag": surp.yield_models.C_AGB_Model(y0=y0, zeta=-y0, tau_agb=1, t_D=0.15),
    }


m_h_lin_break = -1.0
Z_break = surp.gce_math.MH_to_Z(m_h_lin_break)
cc_proxies = {
    "ce": 1e-3,
    "la": surp.yield_models.BiLogLin_CC(y0=-m_h_lin_break * y0, zeta=y0, y1=0), # quadratic
    "ca": surp.yield_models.Quadratic_CC(y0=0, zeta=0, A=y0, Z1=Z_break), # quadratic down to -1
    }

ia_proxies = {}


if __name__ == "__main__":
    proxy_run(agb_proxies, cc_proxies, ia_proxies)
