import sys
import os
from os import path

from surp.simulation.vice_to_json import json_output


directory = sys.argv[1]

for name in os.listdir(directory):
    basename, ext = path.splitext(name)
    if ext == ".vice":
        print("pickle thyme")
        print(name)

        filename = path.join(directory, name)
        print(filename)
        json_output(filename)
