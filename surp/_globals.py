r"""
Global variables to the migration simulations and plot analysis.
"""

END_TIME = 13.2 # total simulation time in Gyr
Z_SUN = 0.016 # Alla Mag++2022
MAX_RADIUS = 20.0

ELEMENTS = ["c", "n", "o", "mg", "fe"]
AGB_MODELS = ["cristallo11", "ventura13", "karakas16", "ritter2018"]

def _find_data_dir():
    """Dynamically determines data directory whe n library is imported"""
    import os
    script_dir = os.path.dirname(__file__)
    rel_path = "../data/"
    abs_path = os.path.join(script_dir, rel_path)
    return abs_path

DATA_DIR = _find_data_dir()


