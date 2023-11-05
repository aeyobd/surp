r"""
Global variables to the migration simulations and plot analysis.
"""

END_TIME = 13.2 # total simulation time in Gyr

# Width of each annulus in kpc
# This needs modified *only* if running the plotting scripts.
ZONE_WIDTH = 0.1

MAX_SF_RADIUS = 15.5 # Radius in kpc beyond which the SFR = 0

# Stellar mass of Milky Way (Licquia & Newman 2015, ApJ, 806, 96)
M_STAR_MW = 5.17e10

N_MAX = 3_102_519

Z_SUN = 0.016


AGB_MODELS = ["cristallo11", "ventura13", "karakas16", "pignatari16"]

# just define shorthands
C11, K10, V13, K16 = AGB_MODELS


def find_data_dir():
    import os
    script_dir = os.path.dirname(__file__)
    rel_path = "../data/"
    abs_path = os.path.join(script_dir, rel_path)
    return abs_path


DATA_DIR = find_data_dir()

