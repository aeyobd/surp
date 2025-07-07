import sys
sys.path.append("..")
from ag_run import ag_run 


import surp
import vice

agb_model = surp.agb_interpolator.interpolator("c")


if __name__ == "__main__":
    ag_run(
        agb_model = agb_model,
        cc_model = 0,
        ia_model = 0,
    )
