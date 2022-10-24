import pandas as pd
import apogee_analysis as aah
import matplotlib.pyplot as plt

def read_skillman20():
    df = pd.read_csv("chaos_m101.dat", sep="\s+")
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
    df = pd.read_csv("md22.csv")
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

def plot_md22(x, y):
    df = read_md22()
    plt.errorbar(df[x], df[y], xerr=df[x + "_err"], yerr=df[y+"_err"], fmt="o", label="M101")


def plot_all(x, y):
    if x in read_skillman20().keys():
        if y in read_skillman20().keys():
            for df in [read_skillman20(), read_md22()]:
                plt.errorbar(df[x], df[y], xerr=df[x + "_err"], yerr=df[y+"_err"], fmt="o", label=df.name)



