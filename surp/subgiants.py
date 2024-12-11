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


def filter_metallicity(df, key="MG_H", c=-0.1, w=0.05):
    """Filter out stars with metallicity outside of [c-w, c+w]
    using the key column for metallicity.
    """

    filt = df[key] >= c - w
    filt &= df[key] < c + w
    return df[filt]


def filter_high_alpha(df):
    """Filter out stars with high alpha abundance
    Assumes DF has a column "high_alpha" that is True for high alpha stars.
    """
    high_alpha = df["high_alpha"]
    return df[~high_alpha]
