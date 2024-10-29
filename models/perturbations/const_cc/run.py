import surp
import vice

import sys
sys.path.append("..")
from ag_run import ag_run 



agb_model = surp.yield_models.ZeroAGB()
cc_model = 0.001
ia_model = 0


if __name__ == "__main__":
    ag_run(
            agb_model = agb_model,
            cc_model = cc_model,
            ia_model = ia_model,
    )
