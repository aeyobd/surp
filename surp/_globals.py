r"""
Global variables to the migration simulations and plot analysis.
"""

END_TIME = 13.2 # total simulation time in Gyr
MAX_RADIUS = 20.0
N_SUBGIANTS = 14_066

# Mag++2022 scale: 
# Z_X = 0.0225 
# Y_ini = 0.2734, X_ini = 0.0176
Z_SUN = 0.0176
Y_SUN  = 0.2734
X_SUN = 0.709 # 1 - Y - Z

ELEMENTS = ["c", "n", "mg", "fe"]

AGB_MODELS = ["cristallo11", "ventura13", "karakas16", "battino19"]

def _find_data_dir():
    """Dynamically determines data directory whe n library is imported"""
    import os
    script_dir = os.path.dirname(__file__)
    rel_path = "../data/"
    abs_path = os.path.join(script_dir, rel_path)
    return abs_path

DATA_DIR = _find_data_dir()


