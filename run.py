import json
import sys
from surp.simulation import multizone_sim
import os

def main():
    if len(sys.argv) != 3:
        raise ValueError("script requires 2 argument, config filename")
    d = sys.argv[1]
    path = sys.argv[2]

    if not os.path.exists(path):
        raise ValueError("path does not exist", path)


    with open(path) as f:
        kwargs = json.load(f)

    print(kwargs)

    multizone_sim.run_model(d, **kwargs)


if __name__ == "__main__":
    main()




