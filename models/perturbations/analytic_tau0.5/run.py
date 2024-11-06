import sys
sys.path.append("..")
from ag_run import ag_run 


import surp
import vice


agb_model = surp.yield_models.C_AGB_Model(y0=0.001, zeta=-0.001, tau_agb=0.5, t_D=0.15)

if __name__ == "__main__":
    ag_run(
        agb_model = agb_model,
        cc_model = 0,
        ia_model = 0,
    )
