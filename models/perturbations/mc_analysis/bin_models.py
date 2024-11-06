import numpy as np
import pandas as pd
from surp import subgiants
from surp import gce_math as gcem
import surp
import os
import sys
import toml

surp.yields.set_magg22_scale()


def main():
    if len(sys.argv) < 2:
        print("Usage: python bin_models.py modeldir")
        sys.exit(1)


    modeldir = sys.argv[1]
    paramfile = modeldir + "/params.toml"

    with open(paramfile) as f:
        params = toml.load(f)

    names = []
    labels = []
    C_H_s = []

    for key, value in params.items():
        names.append(value["name"])
        labels.append(key)
        if "C_H" in value:
            C_H_s.append(value["C_H"])
        else:
            C_H_s.append("AG_H")


    model = make_multicomponent_model(names, labels, C_H_s)
    save_model(modeldir, model)


def load_subgiants():
    df = subgiants.copy()
    df["C_H"] = df["C_FE"] + df["FE_H"]
    df["C_H_ERR"] = df["C_FE_ERR"] + df["FE_H_ERR"]
    df["z_c"] = gcem.brak_to_abund(df["C_H"], "c")
    df["z_c_err"] = np.log(10) * df["C_H_ERR"] * df["z_c"]

    return df

def make_multicomponent_model(names, labels, C_H_s):
    """
    Makes a multi-component model from the given names
    """

    models = [find_model(name, C_H) for name, C_H in zip(names, C_H_s)]

    mg_fe = {label: bin_mg_fe(model)for label, model in zip(labels, models)}
    mg_h = {label: bin_mg_h(model)for label, model in zip(labels, models)}
    bin2d = {label: bin_2d(model) for label, model in zip(labels, models)}


    df = load_subgiants()
    mg_fe_obs = bin_mg_fe(df, x="MG_FE", m_h="MG_H")
    mg_h_obs = bin_mg_h(df, x="MG_H")

    mg_fe = combine_dfs(mg_fe)
    mg_h = combine_dfs(mg_h)

    mg_fe["obs"] = mg_fe_obs.med
    mg_fe["obs_err"] = mg_fe_obs.err
    mg_h["obs"] = mg_h_obs.med
    mg_h["obs_err"] = mg_h_obs.err

    return {
        "mg_fe": mg_fe,
        "mg_h": mg_h,
        }

def combine_dfs(dataframes, special_columns=["x", "counts"]):
    df = {}

    for key, val in dataframes.items():
        df[key] = val.med

        for col in special_columns:
            if col in df.keys():
                assert val[col] == df["_" + col]
            else:
                df["_" + col] = val[col]

    return pd.DataFrame(df)



def save_model(modeldir, model):
    os.makedirs(modeldir, exist_ok=True)
    for key, value in model.items():
        value.to_csv(modeldir + "/" + key + "_binned.csv")



def bin_model(name):
    model = find_model(name)
    mgfe = bin_mg_fe(model)
    mgh = bin_mg_h(model)
    bin2d = bin_2d(model)

    return {
        "mg_fe": mgfe,
        "mg_h": mgh,
        "2d": bin2d
    }



def find_model(name, C_H = "AG_H"):
    """
    Finds the pickled model with either the given name or the parameters 
    and returns the csv summary
    """
    
    file_name = "../" + name + "/stars.csv"
    model =  pd.read_csv(file_name, index_col=0)
    model["z_c"] = gcem.brak_to_abund(model[C_H], "c")
    return model



def bin_2d(df, x="MG_H_true", y="MG_FE_true", val="z_c"):
    mg_bins = np.arange(-1, 0.4, 0.1)
    mg_fe_bins = np.arange(0, 0.41, 0.05)

    df["x_bin"] = pd.cut(df[x], bins=mg_bins, labels=False, include_lowest=True)
    df["y_bin"] = pd.cut(df[y], bins=mg_fe_bins, labels=False, include_lowest=True)

    grouped = df.groupby(["x_bin", "y_bin"])

    results = grouped.agg(
        med=pd.NamedAgg(aggfunc="mean", column=val),
        err=pd.NamedAgg(aggfunc=sde, column=val),        
        xmed=pd.NamedAgg(aggfunc="mean", column=x),
        ymed=pd.NamedAgg(aggfunc="mean", column=y),
        counts=pd.NamedAgg(aggfunc="count", column=val),
    ).reset_index()

    # Create a full grid of all (x_bin, y_bin) combinations
    x_bin_range = range(len(mg_bins)-1)  # Number of x bins
    y_bin_range = range(len(mg_fe_bins)-1)  # Number of y bins
    full_grid = pd.MultiIndex.from_product([x_bin_range, y_bin_range], names=['x_bin', 'y_bin'])
    full_grid_df = full_grid.to_frame(index=False)
    
    df = pd.merge(full_grid_df, results, on=['x_bin', 'y_bin'], how='left')

    x_bin_mids = (mg_bins[:-1] + mg_bins[1:])/2
    y_bin_mids = (mg_fe_bins[:-1] + mg_fe_bins[1:])/2
    
    df["x"] = x_bin_mids[df.x_bin]
    df["y"] = y_bin_mids[df.y_bin]
    
    return df


def sde(x):
    return np.std(x) / np.sqrt(len(x))

def bin_mg_fe(df, x="MG_FE_true", val="z_c", n_min =3, m_h="MG_H_true", m_h_0 = -0.1, d_m_h=0.05):
    mg_bins = np.arange(0, 0.31, 0.05)
    filt = df[m_h] < m_h_0 + d_m_h
    filt &= df[m_h] >= m_h_0 - d_m_h
    df = df[filt].copy()
    df["x_bin"] = pd.cut(df[x], bins=mg_bins, labels=False, include_lowest=True)

    grouped = df.groupby(["x_bin"])

    results = grouped.agg(
        med=pd.NamedAgg(aggfunc="mean", column=val),
        xmed=pd.NamedAgg(aggfunc="mean", column=x),
        err=pd.NamedAgg(aggfunc=sde, column=val),
        counts=pd.NamedAgg(aggfunc="count", column=val),
    ).reset_index()

    x_bin_range = range(len(mg_bins)-1)  # Number of x bins

    full_grid_df = pd.DataFrame({"x_bin": x_bin_range})
    
    df = pd.merge(full_grid_df, results, on=['x_bin'], how='left')
    
    x_bin_mids = (mg_bins[:-1] + mg_bins[1:])/2

    df["x"] = x_bin_mids[df.x_bin]

    df.loc[df.counts < n_min, "med"] = np.nan

    return df

def bin_mg_h(df, x="MG_H_true", val="z_c", n_min =3):
    mg_bins = np.arange(-0.5, 0.4, 0.1)

    df = df[~df.high_alpha].copy()
    df["x_bin"] = pd.cut(df[x], bins=mg_bins, labels=False, include_lowest=True)

    grouped = df.groupby(["x_bin"])

    results = grouped.agg(
        med=pd.NamedAgg(aggfunc="mean", column=val),
        xmed=pd.NamedAgg(aggfunc="mean", column=x),
        err=pd.NamedAgg(aggfunc=sde, column=val),
        counts=pd.NamedAgg(aggfunc="count", column=val),
    ).reset_index()

    x_bin_range = range(len(mg_bins)-1)  # Number of x bins

    full_grid_df = pd.DataFrame({"x_bin": x_bin_range})
    
    df = pd.merge(full_grid_df, results, on=['x_bin'], how='left')
    
    x_bin_mids = (mg_bins[:-1] + mg_bins[1:])/2

    df["x"] = x_bin_mids[df.x_bin]

    df.loc[df.counts < n_min, "med"] = np.nan

    return df


    


if __name__ == "__main__":
    main()

