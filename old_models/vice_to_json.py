"""this script runs the json_output from vice_to_json"""
import sys
import os
import argparse

import surp.simulation.filter_warnings
from surp import ViceModel


def main():
    filename, name, starsname = parse_args()
    model = load_model(filename)
    to_json(model, name)
    save_stars(model, starsname)


def parse_args():
    parser = argparse.ArgumentParser(description="A little script to convert .vice multioutput files to .json and .csv files")
    parser.add_argument("filename", help="thet target path", type=str)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-s", "--stars", type=str, default=None)

    args = parser.parse_args()
    filename = args.filename
    check_filename(filename)

    if args.output is None:
        out, ext = os.path.splitext(os.path.normpath(filename))
    else:
        out  = args.output

    return filename, out, args.stars


def check_filename(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError("file does not exist:", filename)
    filename = os.path.normpath(filename)
    name, ext = os.path.splitext(filename)

    if ext != ".vice":
        raise ValueError("input file must be a vice directory, got", ext)



def load_model(filename):
    print("loading, ", filename)
    return surp.ViceModel.from_vice(filename)


def to_json(model, json_name):
    print("saving to ", json_name)
    model.save(json_name, overwrite=True)
    print("saved")

def save_stars(model, filename):
    print('saving stars at', filename)
    model.stars.to_csv(filename)

if __name__ == "__main__":
    main()
