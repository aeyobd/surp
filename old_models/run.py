import json
import sys
import os
import argparse


from surp.simulation import multizone_sim

def main():
    name, param_file = parse_args()
    with open(param_file) as f:
        kwargs = json.load(f)

    print_kwargs(kwargs)
    multizone_sim.run_model(name, **kwargs)


def parse_args():
    parser = argparse.ArgumentParser(description="Runs a vice model")
    parser.add_argument("name", help="output filename of model", type=str)
    parser.add_argument("params", default="params.json", help="path to parameters", type=str)
    args = parser.parse_args()

    name = args.name
    param_file = args.params
    if not os.path.exists(param_file):
        raise FileNotFoundError("file does not exist:", path)

    return name, param_file



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




