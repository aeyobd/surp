import sys
from .vice_model import vice_model
from os import path
import pandas as pd


def main():
    name = sys.argv[1]
    model = vice_model(name)
    name_out = path.splitext(name)[0] + ".csv"
    data = model.stars[["[o/fe]", "[fe/o]", "[c/o]", "[o/h]"]]
    data.to_csv(name_out)
