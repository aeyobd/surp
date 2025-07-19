import numpy as np
import pandas as pd
from surp import subgiants
from surp import gce_math as gcem
import surp
import os
import sys
import toml

surp.yields.set_magg22_scale()


def add_default(params, key, default):
    if key in params:
        return params[key]
    else:
        params[key] = default
        return default
    

def read_params(paramfile):
    with open(paramfile) as f:
        params = toml.load(f)
    
    add_default(params, "datafile", None)
    add_default(params, "mg_h_bins", np.arange(-0.5, 0.5, 0.04))
    add_default(params, "mg_fe_bins", np.arange(-0.1, 0.4, 0.04))
    add_default(params, "n_min", 3)
    add_default(params, "mg_fe_shift", 0)

    params["mg_h_bins"] = np.array(params["mg_h_bins"])
    params["mg_fe_bins"] = np.array(params["mg_fe_bins"])
    return params


def main():
    if len(sys.argv) < 2:
        print("Usage: python bin_models.py modeldir")
        sys.exit(1)


    modeldir = sys.argv[1]
    paramfile = modeldir + "/params.toml"

    params = read_params(paramfile)

    names = []
    labels = []
    C_MG_s = []
    y_shifts = []

    for key, value in params.items():
        if key == "sigma_int":
            continue
        if type(value) != dict:
            continue
        names.append(value["name"])
        labels.append(key)
        if "C_MG" in value:
            C_MG_s.append(value["C_MG"])
        else:
            C_MG_s.append("AG_MG")

        if "y_shift" in value:
            y_shifts.append(value["y_shift"])
        else:
            y_shifts.append(0)

    model = make_multicomponent_model(names, labels, C_MG_s, 
        datafile=params["datafile"], 
        mg_h_bins = params["mg_h_bins"],
        mg_fe_bins = params["mg_fe_bins"],
        n_min = params["n_min"],
        mg_fe_shift = params["mg_fe_shift"],

    )

    models_const = model.y0_cc

    for shift, label in zip(y_shifts, labels):
        if shift != 0:
            dy = models_const * shift 
            model[label] += dy

    save_model(modeldir, model)


def load_observations(datafile=None):

    if datafile is None:
        df = subgiants.copy()
    elif datafile == "vincenzo+2021":
        df = surp.vincenzo2021()
    else:
        df = pd.read_csv(datafile)

    df["z_c"] = gcem.brak_to_abund_ratio(df["C_MG"], "c", "mg")
    df["z_c_err"] = np.log(10) * df["C_MG_ERR"] * df["z_c"]

    return df

def make_multicomponent_model(names, labels, C_MG_s, *, 
        datafile, mg_h_bins, mg_fe_bins, 
        n_min, mg_fe_shift
    ):
    """
    Makes a multi-component model from the given names
    """

    models = [find_model(name, C_MG, mg_fe_shift=mg_fe_shift) for name, C_MG in zip(names, C_MG_s)]

    bin2d = {label: bin_2d(model, mg_fe_bins=mg_fe_bins, mg_h_bins=mg_h_bins, n_min=n_min) for label, model in zip(labels, models)}

    df = load_observations(datafile)
    bin2d_obs = bin_2d(df, x="MG_H", y="MG_FE", mg_h_bins=mg_h_bins, mg_fe_bins=mg_fe_bins, n_min=n_min)

    bin2d = combine_dfs(bin2d, special_columns=["x", "y", "counts"])

    bin2d["obs"] = bin2d_obs["mean"]
    bin2d["obs_sem"] = bin2d_obs["sem"]
    bin2d["obs_counts"] = bin2d_obs.counts



    N = len(bin2d)
    bin2d = bin2d.dropna()
    dN = N - len(bin2d)
    print(f"Removed {dN}  / {N} bins from 2d")


    return bin2d

def combine_dfs(dataframes, special_columns=["x", "counts"]):
    df = {}

    for key, val in dataframes.items():
        df[key] = val["mean"]
        df[f"{key}_sem"] = val["sem"]

        for col in special_columns:
            if col in df.keys():
                assert val[col] == df["_" + col]
            else:
                df["_" + col] = val[col]

    return pd.DataFrame(df)



def save_model(modeldir, model):
    os.makedirs(modeldir, exist_ok=True)
    model.to_csv(modeldir + "/" + "2d" + "_binned.csv")



def bin_model(name):
    model = find_model(name)
    bin2d = bin_2d(model)

    return bin2d



def find_model(name, C_MG = "AG_MG", mg_fe_shift=0):
    """
    Finds the pickled model with either the given name or the parameters 
    and returns the csv summary
    """
    
    file_name = "../" + name + "/stars.csv"
    model =  pd.read_csv(file_name, index_col=0)
    model["z_c"] = gcem.brak_to_abund_ratio(model[C_MG], "c", "mg")
    model["MG_FE"] += mg_fe_shift
    model["MG_FE"] += mg_fe_shift
    return model



def bin_2d(df, x="MG_H", y="MG_FE", val="z_c",
    mg_h_bins = np.arange(-1, 0.4, 0.1),
    mg_fe_bins = np.arange(0, 0.41, 0.05),
    n_min = 3
           ):

    df["x_bin"] = pd.cut(df[x], bins=mg_h_bins, labels=False, include_lowest=True)
    df["y_bin"] = pd.cut(df[y], bins=mg_fe_bins, labels=False, include_lowest=True)

    grouped = df.groupby(["x_bin", "y_bin"])

    results = grouped.agg(
        mean=pd.NamedAgg(aggfunc="mean", column=val),
        std=pd.NamedAgg(aggfunc="std", column=val),        
        xmean=pd.NamedAgg(aggfunc="mean", column=x),
        ymean=pd.NamedAgg(aggfunc="mean", column=y),
        counts=pd.NamedAgg(aggfunc="count", column=val),
    ).reset_index()


    # Create a full grid of all (x_bin, y_bin) combinations
    x_bin_range = range(len(mg_h_bins)-1)  # Number of x bins
    y_bin_range = range(len(mg_fe_bins)-1)  # Number of y bins
    full_grid = pd.MultiIndex.from_product([x_bin_range, y_bin_range], names=['x_bin', 'y_bin'])
    full_grid_df = full_grid.to_frame(index=False)
    
    df = pd.merge(full_grid_df, results, on=['x_bin', 'y_bin'], how='left')

    x_bin_mids = (mg_h_bins[:-1] + mg_h_bins[1:])/2
    y_bin_mids = (mg_fe_bins[:-1] + mg_fe_bins[1:])/2
    
    df["x"] = x_bin_mids[df.x_bin]
    df["y"] = y_bin_mids[df.y_bin]

    df.loc[df.counts < n_min, "med"] = np.nan
    df.loc[df.counts < n_min, "err"] = np.nan
    df["sem"] = df["std"] / np.sqrt(df.counts)
    
    return df


if __name__ == "__main__":
    main()

