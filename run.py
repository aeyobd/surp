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

    print_kwargs(kwargs)


    multizone_sim.run_model(d, **kwargs)

def print_kwargs(kwargs):
    print()
    w = 16
    print(f"{'keys':16}\t{'values':16}")
    print("-"*w + "\t" + "-"*w)
    for key, arg in kwargs.items():
        if key == "yield_kwargs":
            continue
        arg = str(arg)
        print(f"{key:16s}\t{arg:16s}")
    print()
    print("yield_kwargs")
    print("-"*w)
    for key, arg in kwargs["yield_kwargs"].items():
        arg = str(arg)
        print(" "*4, f"{key:12}    {arg:16}")
    print()

    print("-"*(2*w+8))
    print()

if __name__ == "__main__":
    main()




