from surp.vice_to_pickle import pickle_output
import multizone_sim
import sys
import os

directory = sys.argv[1]

for name in os.listdir(directory):
    if name[-5:] == ".vice":
        print("pickle thyme")
        print(name)
        pickle_name = directory +  name[:-5] + ".pickle"
        file_name = directory + name
        print(file_name)
        pickle_output(file_name, pickle_name = pickle_name)


