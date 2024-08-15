import os
import pandas as pd

from ._globals import DATA_DIR


def _read_subgiants():
    abs_path = DATA_DIR + "subgiants.csv"

    if os.path.exists(abs_path):
        subgiants = pd.read_csv(abs_path, index_col=0, dtype={"MEMBER": str})
    else:
        print("warning could not find subgiants at ", abs_path) 
        subgiants = None

    return subgiants

