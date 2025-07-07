import surp
import vice

import sys
sys.path.append("..")
from ag_run import ag_run 



agb_model = surp.agb_interpolator.interpolator("c", study="karakas16")
cc_model = 0.0
ia_model = 0


if __name__ == "__main__":
    ag_run(
            agb_model = agb_model,
            cc_model = cc_model,
            ia_model = ia_model,
    )
