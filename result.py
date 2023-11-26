import sys
from os import path

from surp import ViceModel


def main():
    for name in sys.argv[1:]:
        name_out = path.splitext(name)[0] + ".csv"
        if path.exists(name_out):
            print("skipping: ", name)
            continue

        if not path.exists(name):
            raise IOError("file not found: ", name)

        print("loading model: ", name)
        model = ViceModel(name)
        data = model.stars[["[o/fe]", "[c/o]", "[o/h]", "[c/n]"]]

        print("writing")
        data.to_csv(name_out)

        print("saved to ", name_out)


if __name__ == "__main__":
    main()
