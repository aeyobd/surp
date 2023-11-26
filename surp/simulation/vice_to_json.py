import vice
import pandas as pd
import numpy as np
import random
from os import path
import json
from .._globals import MAX_SF_RADIUS, DATA_DIR

from .vice_utils import load_model, zone_to_R

# these are not used but pickles
# won't behave otherwise
import surp
from surp.simulation import multizone_sim
from surp import yields






if __name__ == "__main__":
    json_output(sys.argv[1] + "*", json_name=None, isotopic=False, overwrite=False)

