import pandas as pd
import matplotlib.pyplot as plt
import surp

import surp.gce_math as gcem
import arya
import vice
import numpy as np
import sys

sys.path.append("..")

from mc_plot_utils import MCMCResult
import mc_plot_utils



yagb_props = {}

df = pd.read_csv("../yield_fits.tsv", sep=r"\s+", comment="#")

for _, row in df.iterrows():
    yagb_props[row.model] = {
        "y0": row.y0 * 1e-4,
        "y_a": row.zeta0 * 1e-4,
        "zeta_a": row.zeta1 * 1e-4,
    }

yagb_props["analytic"] = {
    "y0": 1e-3,
    "y_a": 1e-3,
    "zeta_a": 1e-3
}

def load_model(filename, props, test=False, burn=0):
    y0 = props["y0"],
    y_a = props["y_a"]
    zeta_a = props["zeta_a"]
    
    if test:
        result = MCMCResult.from_test_file(filename, burn=burn)
    else:
        result = MCMCResult.from_file("../../models/mcmc_models_2d/" + filename + "/", y0=y0, burn=burn, y_a=y_a, zeta_a=zeta_a)
    return result




results = {}

results["fruity"] = load_model("fiducial_constrained", yagb_props["fruity"])
#results["fruity"] = load_model("fiducial", yagb_props["fruity"])
results["fruity_mf0.7"] = load_model("fruity_mf0.7_constrained", yagb_props["fruity_mf0.7"])
results["aton"] = load_model("aton_constrained", yagb_props["aton"])
results["nugrid"] = load_model("nugrid_constrained", yagb_props["nugrid"])
results["monash"] = load_model("monash_constrained", yagb_props["monash"])

results["lateburst"] = load_model("lateburst_constrained", yagb_props["fruity"])
results["twoinfall"] = load_model("twoinfall_constrained", yagb_props["fruity"])
results["eta2"] = load_model("eta2_constrained", yagb_props["fruity"])
#results["sneia_1.2"] = load_model("sneia_1.2_constrained", yagb_props["fruity"])

