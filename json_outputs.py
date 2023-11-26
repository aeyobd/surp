"""this script runs the json_output from vice_to_json"""

import sys
import os
from os import path

import surp.simulation.filter_warnings
from surp.simulation.vice_to_json import json_output

def main():
    if len(sys.argv) < 2:
        sys.exit("script requires at least 1 argument (filename)")

    filename = sys.argv[1]
    basename, ext = path.splitext(filename)
    if ext != ".vice":
        raise ValueError("input file must be a vice directory")
    print("jsoning ", filename)
    json_output(filename)

if __name__ == "__main__":
    main()
