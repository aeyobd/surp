import sys
import vice

import surp.osc.yields
from surp.osc.yields import set_yields

import surp.src.simulation.multizone_sim
from surp.src.simulation.multizone_sim import run_model
from surp import __version__

def main(prefix, filename, eta=1, beta=0.001, spec="insideout",
         f_agb=0.2, OOB=False, agb_model="C11", A=1.5, 
         fe_ia_factor=1, traditional_f=False,
         alpha_n=0.5, dt=0.01, n_stars=2, post_process=False):

    print("Loaded")
    agb_model = {
            "C11": "cristallo11",
            "K10": "karakas10",
            "V13": "ventura13",
            "K16": "karakas16"
            }[agb_model]

    set_yields(eta=eta, beta=beta, fe_ia_factor=fe_ia_factor,
        agb_model=agb_model, oob=OOB, f_agb=f_agb, alpha_n=alpha_n)


    if post_process:
        mm = "post-process"
    else:
        mm = "diffusion"
    print("configured")

    run_model(filename, prefix=prefix,
              eta_factor=eta, 
              spec=spec, 
              burst_size=A, 
              dt=dt, 
              n_stars=n_stars,
              migration_mode=mm,
              )
    print("complete")





