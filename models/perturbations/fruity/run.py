import sys
sys.path.append("..")
from ag_run import ag_run 


import surp
import vice


ag_run(
    agb_model = surp.agb_interpolator.interpolator("c"),
    cc_model = 0,
    ia_model = 0,
)
