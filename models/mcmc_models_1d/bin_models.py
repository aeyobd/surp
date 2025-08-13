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
    add_default(params, "mg_h_bins", np.linspace(-0.4, 0.3, 20))
    add_default(params, "mg_fe_bins", np.linspace(0.025, 0.25, 12))
    add_default(params, "mg_fe_n_min", 3)
    add_default(params, "mg_h_n_min", 3)
    add_default(params, "m_h_0", -0.1)
    add_default(params, "d_m_h", 0.05)
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
        mg_fe_bins = params["mg_fe_bins"],
        mg_h_bins = params["mg_h_bins"],
        mg_fe_n_min = params["mg_fe_n_min"],
        mg_h_n_min = params["mg_h_n_min"],
        m_h_0 = params["m_h_0"],
        d_m_h = params["d_m_h"],
        mg_fe_shift = params["mg_fe_shift"],

    )


    for shift, label in zip(y_shifts, labels):
        if shift != 0:
            models_const = {key: val.y0_cc for key, val in model.items()}
            for group in models_const.keys():
                dy = models_const[group] * shift 
                model[group][label] += dy

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
        datafile, mg_h_bins, mg_fe_bins, m_h_0, d_m_h,
        mg_fe_n_min, mg_h_n_min, mg_fe_shift
    ):
    """
    Makes a multi-component model from the given names
    """

    mg_fe_kwargs = {
        "n_min": mg_fe_n_min,
        "mg_fe_bins": mg_fe_bins,
        "m_h_0": m_h_0,
        "d_m_h": d_m_h
        }
    mg_h_kwargs = {
        "n_min": mg_h_n_min,
        "mg_h_bins": mg_h_bins,
        }

    models = [find_model(name, C_MG, mg_fe_shift=mg_fe_shift) for name, C_MG in zip(names, C_MG_s)]

    mg_h = {label: bin_mg_h(model, **mg_h_kwargs) for label, model in zip(labels, models)}
    mg_fe = {label: bin_mg_fe(model, **mg_fe_kwargs) for label, model in zip(labels, models)}

    df = load_observations(datafile)
    mg_fe_obs = bin_mg_fe(df, x="MG_FE", m_h="MG_H", **mg_fe_kwargs)
    mg_h_obs = bin_mg_h(df, x="MG_H", **mg_h_kwargs)

    mg_fe = combine_dfs(mg_fe)
    mg_h = combine_dfs(mg_h)

    mg_fe["obs"] = mg_fe_obs.med
    mg_fe["obs_err"] = mg_fe_obs.err
    mg_fe["obs_counts"] = mg_fe_obs.counts
    mg_h["obs"] = mg_h_obs.med
    mg_h["obs_err"] = mg_h_obs.err
    mg_h["obs_counts"] = mg_h_obs.counts

    N = len(mg_h)
    mg_h = mg_h.dropna()
    dN = N - len(mg_h)
    print(f"Removed {dN} bins from mg_h")
    N = np.sum(~models[0].high_alpha)
    Nf = np.nansum(mg_h["_counts"])
    print(f"Fraction of stars in bins: {Nf} / {N}")
    N = np.sum(~df.high_alpha)
    Nf = np.nansum(mg_h["obs_counts"])
    print(f"Fraction of observed in bins: {Nf} / {N}")

    N = len(mg_fe)
    mg_fe = mg_fe.dropna()
    dN = N - len(mg_fe)
    print(f"Removed {dN} bins from mg_fe")
    N = np.sum((models[0].MG_H_true < m_h_0 + d_m_h) & (models[0].MG_H_true >= m_h_0 - d_m_h))
    Nf = np.nansum(mg_fe["_counts"])
    print(f"Fraction of stars in bins: {Nf} / {N}")
    filt = (df.MG_H < m_h_0 + d_m_h) & (df.MG_H >= m_h_0 - d_m_h)
    N = np.sum(filt)
    Nf = np.nansum(mg_fe["obs_counts"])
    print(f"Fraction of observed in bins: {Nf} / {N}")



    return {
        "mg_fe": mg_fe,
        "mg_h": mg_h,
        }

def combine_dfs(dataframes, special_columns=["x", "counts"]):
    df = {}

    for key, val in dataframes.items():
        df[key] = val.med
        df[f"{key}_err"] = val.err

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

    return {
        "mg_fe": mgfe,
        "mg_h": mgh,
    }



def find_model(name, C_MG = "AG_MG", mg_fe_shift=0):
    """
    Finds the pickled model with either the given name or the parameters 
    and returns the csv summary
    """
    
    file_name = "../" + name + "/stars.csv"
    model =  pd.read_csv(file_name, index_col=0)
    model["z_c"] = gcem.brak_to_abund_ratio(model[C_MG], "c", "mg")
    model["MG_FE_true"] += mg_fe_shift
    model["MG_FE"] += mg_fe_shift
    return model




def bin_mg_fe(df, x="MG_FE_true", val="z_c", 
        n_min =3, m_h="MG_H_true",
        m_h_0 = -0.1, d_m_h=0.05, 
        mg_fe_bins = np.arange(-1, 0.4, 0.1)
        ):

    filt = df[m_h] < m_h_0 + d_m_h
    filt &= df[m_h] >= m_h_0 - d_m_h
    df = df[filt].copy()
    df["x_bin"] = pd.cut(df[x], bins=mg_fe_bins, labels=False, include_lowest=True)

    grouped = df.groupby(["x_bin"])

    results = grouped.agg(
        med=pd.NamedAgg(aggfunc="mean", column=val),
        xmed=pd.NamedAgg(aggfunc="mean", column=x),
        err=pd.NamedAgg(aggfunc="std", column=val),
        counts=pd.NamedAgg(aggfunc="count", column=val),
    ).reset_index()

    x_bin_range = range(len(mg_fe_bins)-1)  # Number of x bins

    full_grid_df = pd.DataFrame({"x_bin": x_bin_range})
    
    df = pd.merge(full_grid_df, results, on=['x_bin'], how='left')
    
    x_bin_mids = (mg_fe_bins[:-1] + mg_fe_bins[1:])/2

    df["x"] = x_bin_mids[df.x_bin]

    df.loc[df.counts < n_min, "med"] = np.nan

    return df


def bin_mg_h(df, x="MG_H_true", val="z_c", n_min =3, mg_h_bins = np.arange(-1, 0.4, 0.1)):

    df = df[~df.high_alpha].copy()
    df["x_bin"] = pd.cut(df[x], bins=mg_h_bins, labels=False, include_lowest=True)

    grouped = df.groupby(["x_bin"])

    results = grouped.agg(
        med=pd.NamedAgg(aggfunc="mean", column=val),
        xmed=pd.NamedAgg(aggfunc="mean", column=x),
        err=pd.NamedAgg(aggfunc="std", column=val),
        counts=pd.NamedAgg(aggfunc="count", column=val),
    ).reset_index()

    x_bin_range = range(len(mg_h_bins)-1)  # Number of x bins

    full_grid_df = pd.DataFrame({"x_bin": x_bin_range})
    
    df = pd.merge(full_grid_df, results, on=['x_bin'], how='left')
    
    x_bin_mids = (mg_h_bins[:-1] + mg_h_bins[1:])/2

    df["x"] = x_bin_mids[df.x_bin]

    df.loc[df.counts < n_min, "med"] = np.nan

    return df


    


if __name__ == "__main__":
    main()

