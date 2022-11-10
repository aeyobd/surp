import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import vice

from . import apogee_analysis as aah
from . import plotting_utils as pluto


def get_path(name):
    script_dir = os.path.dirname(__file__)
    rel_path = "../../data/" + name
    abs_path = os.path.join(script_dir, rel_path)
    return abs_path

def read_skillman20():
    script_dir = os.path.dirname(__file__)
    rel_path = "../../data/chaos_m101.dat"
    abs_path = os.path.join(script_dir, rel_path)

    df = pd.read_csv(abs_path, sep="\s+")
    df1 = pd.DataFrame()
    df1["[o/h]"] = aah.log_to_bracket(df["O_H"], "o") - 12
    df1["[c/o]"] = aah.log_to_bracket(df["C_O"], "c", "o")
    df1["[c/n]"] = aah.log_to_bracket(df["C_N"], "c", "n")
    df1["[n/o]"] = df1["[c/o]"] - df1["[c/n]"]

    df1["[o/h]_err"] = df["O_H_err"]
    df1["[c/o]_err"] = df["C_O_err"] * 12/16
    df1["[c/n]_err"] = df["C_N_err"] * 12/14
    df1["[n/o]_err"] = df["C_O_err"] + df["C_N_err"]

    df1.name="M101"
    return df1

def plot_skillman20(x, y):
    s20 = read_skillman20()
    plt.errorbar(s20[x], s20[y], xerr=s20[x + "_err"], yerr=s20[y+"_err"], fmt="o", label="M101")


def read_md22():
    script_dir = os.path.dirname(__file__)
    rel_path = "../../data/md22.csv"
    abs_path = os.path.join(script_dir, rel_path)
    df = pd.read_csv(abs_path)
    df1 = pd.DataFrame()
    df1["[o/h]"] = aah.log_to_bracket(df["O_H"], "o") - 12

    df1["[c/h]"] = aah.log_to_bracket(df["C_H"], "c") - 12
    df1["[n/h]"] = aah.log_to_bracket(df["N_H"], "n") - 12

    df1["[c/n]"] = df1["[c/h]"] - df1["[n/h]"]
    df1["[c/o]"] = df1["[c/h]"] - df1["[o/h]"]
    df1["[n/o]"] = df1["[n/h]"] - df1["[o/h]"]

    df1["[o/h]_err"] = df["O_H_err"]
    df1["[c/o]_err"] = df["C_H_err"] + df["O_H_err"]
    df1["[n/o]_err"] = df["N_H_err"] + df["O_H_err"]
    df1["[c/n]_err"] = df["C_H_err"] + df["N_H_err"]

    df1.name = "Milkyway"
    return df1

def read_cooke17():
    cooke17 = pd.read_csv(get_path("cooke17.csv"))

    cooke17["[c/o]"] = cooke17.c_o
    cooke17["[c/o]_err"] = cooke17.c_o_err
    cooke17["[o/h]"] = cooke17.o_h
    cooke17["[o/h]_err"] = cooke17.o_h_err

    return cooke17

def read_berg19():
    script_dir = os.path.dirname(__file__)
    rel_path = "../../data/berg19.csv"
    abs_path = os.path.join(script_dir, rel_path)
    berg19 = pd.read_csv(abs_path)
    berg19 = berg19.iloc[:-1] 
    berg19["[c/o]"] = berg19.log_c_o + np.log10(12/16) - np.log10(vice.solar_z("c")/vice.solar_z("o"))
    berg19["[o/h]"] = berg19.eps_o + np.log10(16) - np.log10(vice.solar_z("o")) - 12

    berg19["[c/o]_err"] = berg19.log_c_o_err
    berg19["[o/h]_err"] = berg19.eps_o_err

    return berg19

def read_RL():
    RL = pd.read_csv(get_path("extragalactic_RL.csv"), sep="\t+")
    RL["[c/o]"] = aah.log_to_bracket(RL.eps_c - RL.eps_o,
                                                   "c", "o")
    RL["[o/h]"] = aah.log_to_bracket(RL.eps_o, "o") - 12
    RL["[c/o]_err"] = RL.c_err + RL.o_err
    RL["[o/h]_err"] = RL.o_err 

    return RL


def plot_gas():
    RL = read_RL()
    berg = read_berg19()
    mw = read_md22()
    m101 = read_skillman20()
    cooke17 = read_cooke17()
    all_abundances = pd.DataFrame(columns=["[c/o]", "[c/o]_err", "[o/h]",
                                           "[o/h]_err", "type"])


    for df, label in [(RL, "HII"), (berg, "dwarf"), (m101, "HII"), (mw, "HII"),
                        (cooke17, "DLA")]:
        all_abundances = all_abundances.append(pd.DataFrame({
                    "[c/o]": df["[c/o]"],
                    "[c/o]_err": df["[c/o]_err"],
                    "[o/h]": df["[o/h]"],
                    "[o/h]_err": df["[o/h]_err"],
                    "type": [label]*len(df)
                }), ignore_index=True)


    for i in range(3):
        val = ["HII", "dwarf", "DLA"][i]
        df = all_abundances[all_abundances.type == val]
        plt.scatter(df["[o/h]"], df["[c/o]"], label=val,
                    marker=["o", "d", "*", "^"][i])


    return all_abundances

def plot_md22(x, y):
    df = read_md22()
    plt.errorbar(df[x], df[y], xerr=df[x + "_err"], yerr=df[y+"_err"], fmt="o", label="M101")


def plot_all(x, y, **kwargs):
    if x in read_skillman20().keys():
        if y in read_skillman20().keys():
            for df in [read_skillman20(), read_md22()]:
                pluto.err_scatter(df[x], df[y], xerr=df[x + "_err"], yerr=df[y+"_err"], label=df.name, **kwargs)
