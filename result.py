import sys
from surp.analysis.vice_model import vice_model
from os import path
import pandas as pd


def main():
    for name in sys.argv[1:]:
        name_out = path.splitext(name)[0] + ".csv"
        if path.exists(name_out):
            print("skipping: ", name)
            continue

        if not path.exists(name):
            raise IOError("file not found: ", name)

        print("loading model: ", name)
        model = vice_model(name)
        data = model.stars[["[o/fe]", "[fe/o]", "[c/o]", "[o/h]", "[n/o]"]]
        print("writing")
        data.to_csv(name_out)
        print("saved to ", name_out)


if __name__ == "__main__":
    main()
