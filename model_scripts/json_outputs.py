import sys
import os


sys.path.append("../..")
from surp.model_scripts.vice_to_json import json_output
from surp.model_scripts import multizone_sim


directory = sys.argv[1]

for name in os.listdir(directory):
    if name[-5:] == ".vice":
        print("pickle thyme")
        print(name)
        json_name = directory +  name[:-5] + ".json"
        file_name = directory + name
        print(file_name)
        json_output(file_name, json_name = json_name)
