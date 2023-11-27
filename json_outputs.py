"""this script runs the json_output from vice_to_json"""

import sys
import os
from os import path

import surp.simulation.filter_warnings
from surp import ViceModel

def main():
    if len(sys.argv) != 2:
        sys.exit("script requires 1 argument (filename)")

    filename = sys.argv[1]
    basename, ext = path.splitext(filename)
    print(filename)

    if ext != ".vice":
        raise ValueError("input file must be a vice directory, got", ext)


    model = load_model(filename)

    json_name = basename + ".json"
    to_json(model, json_name)

    result_name = basename + ".csv"
    result(model, result_name)


def result(model, filename):
    data = model.stars[["[o/fe]", "[c/o]", "[o/h]", "[n/o]", "[c/n]"]]
    print("saving result to ", filename)

    data.to_csv(filename)
    print("saved")


def load_model(filename):
    print("loading ", filename)
    model = ViceModel.from_vice(filename)

    return model


def to_json(model, json_name):
    print("saving to ", json_name)
    model.save(json_name, overwrite=True)
    print("saved")


if __name__ == "__main__":
    main()
