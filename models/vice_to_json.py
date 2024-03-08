"""this script runs the json_output from vice_to_json"""
import sys
import os
import argparse

from surp import ViceModel, MWParams


def main():
    args = parse_args()

    filename = args.filename
    check_filename(filename)

    params = MWParams.from_file(args.parameters)

    if args.output is None:
        out, ext = os.path.splitext(os.path.normpath(filename))
    else:
        out  = args.output


    model = load_model(filename, params.zone_width)
    to_json(model, args.output)
    save_stars(model, args.stars)



def parse_args():
    parser = argparse.ArgumentParser(description="A little script to convert .vice multioutput files to .json and .csv files")
    parser.add_argument("filename", help="thet target path", type=str)
    parser.add_argument("-o", "--output", type=str, default="model.json")
    parser.add_argument("-s", "--stars", type=str, default="stars.csv")
    parser.add_argument("-p", "--parameters", type=str, default="params.json")

    args = parser.parse_args()
    return args


def check_filename(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError("file does not exist:", filename)
    filename = os.path.normpath(filename)
    name, ext = os.path.splitext(filename)

    if ext != ".vice":
        raise ValueError("input file must be a vice directory, got", ext)



def load_model(filename, zone_width):
    print("loading, ", filename)
    return ViceModel.from_vice(filename, zone_width)


def to_json(model, json_name):
    print("saving to ", json_name)
    model.save(json_name, overwrite=True)
    print("saved")

def save_stars(model, filename):
    print('saving stars at', filename)
    model.stars.to_csv(filename)

if __name__ == "__main__":
    main()
