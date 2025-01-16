import re
import os
import numpy as np
import pandas as pd
import vice

import surp
from ._globals import ELEMENTS, DATA_DIR, N_SUBGIANTS


def load_vice(name, zone_width, migration_data=None):
    """
    load_vice(name, zone_width, migration_data=None)

    Loads a vice.milkyway model output at the location name.

    Parameters
    ----------
    name : str
        the name of the model to load
    migration_data : str
        The mode in which to read the migration data. 
        May be "analytic" or "hydrodisk".
    zone_width : float
        The width of the zones to convert to R (assumed linear...)

    Returns
    -------
    vice.multioutput file
    """

    milkyway = vice.output(name)
    if migration_data == "hydrodisk":
        milkyway.stars["abs_z"] = calculate_z(milkyway)
    elif migration_data == "analytic":
        df = get_analytic_migration_ini_fin("migration_initial_final.dat")
        df.set_index(["i", "zone", "n"], inplace=True)
        df.sort_index(inplace=True)
        milkyway.stars["abs_z"] = np.abs(df["z_final"].values)
        milkyway.stars["R_origin"] = df["R_birth"].values
        milkyway.stars["R_final"] = df["R_final"].values
    else:
        milkyway.stars["abs_z"] = [0 for _ in milkyway.stars["zone_origin"]]

    if migration_data != "analytic":
        milkyway.stars["R_origin"] = zone_to_R(milkyway.stars["zone_origin"], zone_width)
        milkyway.stars["R_final"] = zone_to_R(milkyway.stars["zone_final"], zone_width)

    return milkyway



def reduce_history(multioutput, zone_width):
    """
    reduce_history(multioutput, zone_width)

    Returns a pandas DF object representing the entire history class
    """
    history_cols = multioutput.zones["zone0"].history.keys()
    history_cols += ["R", "zone"]
    history = pd.DataFrame() #columns=history_cols)

    mdf_cols = multioutput.zones["zone0"].mdf.keys()
    mdf_cols += ["R", "zone"]
    mdf = pd.DataFrame() #columns=mdf_cols)

    keys = multioutput.zones.keys()
    N = len(keys)
    for i in range(N):
        zone = multioutput.zones[keys[i]]
        zone_idx = _zone_to_int(keys[i])
        R = zone_to_R(zone_idx, zone_width=zone_width)

        df = pd.DataFrame(zone.history.todict())
        df["R"] = np.repeat(R, len(df))
        df["zone"] = np.repeat(zone_idx, len(df))
        history = pd.concat((history, df), ignore_index=True)

        df = pd.DataFrame(zone.mdf.todict())
        df["R"] = np.repeat(R, len(df))
        df["zone"] = np.repeat(zone_idx, len(df))
        mdf = pd.concat((mdf, df), ignore_index=True)
    
    history = rename_columns(history)
    drop_z_cols(history)
    history = order_abundance_ratios(history)
    return history, mdf



def _zone_to_int(zone: str):
    """
    _zone_to_int(zone: str)

    Converts a zone string (format e.g. "zone15") to an integer.
    """
    matches = re.findall(r'\d+', zone)

    if len(matches) != 1:
        raise Exception("expected only one number in zone, instead got ", matches)

    i = int(matches[0])

    if i < 0:
        raise Exception("expected zone number to be positive, got, ", i)

    return i


def ssp_weight(mass, metallicity, age):
    """A functional form for the weight of finding a sampled star from an SSP given its age and metallicity"""

    return mass


def reduce_stars(multioutput, *,  weight_function=ssp_weight):
    """
    reduce_stars(multioutput)

    Returns a pandas DF object representing the entire stars class.
    Additionally, renames abundances to be in apogee-like format

    weight_function : function = ssp_weight
        A function that takes in np vectors of mass, metallicity, and age
        and returns a weight for each star in the sample.
    """
    df = pd.DataFrame(multioutput.stars.todict())
    df = rename_columns(df)
    drop_z_cols(df)
    df = order_abundance_ratios(df)
    df["high_alpha"] = surp.gce_math.is_high_alpha(df.MG_FE, df.MG_H)
    df["weight"] = weight_function(df.mass, df.FE_H, df.age)

    return df

# APOGEE DR17 pipeline (Holzman et al.) is not published yet
# These are simple fits to the reported uncertanties
# for the subgiant sample.

def polynomial(x, coeffs):
    s = 0
    N = len(coeffs)
    for i in range(N):
        power = (N - i - 1)
        s += coeffs[i] * x**(N - i - 1)
    return s


def fe_h_err(Fe_H):
    return np.maximum(0.005, polynomial(Fe_H, [-0.00557748, 0.00831548]))

def c_mg_err(Fe_H):
    return np.maximum(0.01, polynomial(Fe_H, [-0.03789911, 0.03505672]))

def mg_h_err(Fe_H):
    return np.maximum(0.01, polynomial(Fe_H,[0.06521454,0.00522015,0.03381753]))


def mg_fe_err(Fe_H):
    return np.maximum(0.005, polynomial(Fe_H,[ 0.00792663,-0.00801737, 0.0138201 ]))


def create_star_sample(stars, cdf = None, num=N_SUBGIANTS, 
        zone_width=0.1, seed=-1, 
        c_mg_err=c_mg_err, mg_h_err=mg_h_err, mg_fe_err=mg_fe_err,
        ):
    """
    creates a sample of stars given a dataframe of vice stars.

    Parameters
    ----------
    stars : pd.DataFrame
        The dataframe of stars to sample from. Expected to have columns
        - R_final
        - C_MG
        - MG_H
        - MG_FE
        - FE_H
    cdf : pd.DataFrame
        The CDF of radii for the subgiants. Should have columns "R" and "cdf".


    """
    if cdf is None:
        cdf = load_cdf()


    if seed >= 0:
        rng = np.random.default_rng(seed)
        print("setting seed to ", seed)
    else:
        rng = np.random.default_rng()

    sample = pd.DataFrame()
    for _ in range(num):
        sample = pd.concat((sample, rand_star(stars, cdf, zone_width, rng=rng)), ignore_index=True)

    sample["C_MG_true"] = sample.C_MG
    sample["MG_H_true"] = sample.MG_H
    sample["MG_FE_true"] = sample.MG_FE
    sample["FE_H_true"] = sample.FE_H

    MH = sample.FE_H
    sample["C_MG_err"] = c_mg_err(MH)
    sample["MG_H_err"] = mg_h_err(MH)
    sample["MG_FE_err"] = mg_fe_err(MH)

    N = len(sample)
    sample.C_MG += rng.normal(0, sample.C_MG_err, N)
    sample.MG_H += rng.normal(0, sample.MG_H_err, N)
    sample.MG_FE += rng.normal(0, sample.MG_FE_err, N)

    return sample


@np.vectorize
def R_to_zone(r, zone_width):
    return int(np.floor(r/zone_width))

@np.vectorize
def zone_to_R(zone, zone_width):
    return (zone + 1/2) * zone_width


def ele_columns():
    """Returns a list of all possible element columns in the form of apogee_names in the ideal order."""
    cols = []
    N = len(ELEMENTS)

    for i in range(N):
        ele = ELEMENTS[i]
        for j in range(i, N):
            if j == i:
                ele2 = "H"
            else:
                ele2 = ELEMENTS[j]
            cols.append(f"{ele}_{ele2}".upper()) # apogee_names
    return cols


def new_name(col):
    new_col = col.upper()
    new_col = new_col.replace("[", "")
    new_col = new_col.replace("]", "")
    new_col = new_col.replace("/", "_")
    return new_col


def invert_name(col):
    eles = extract_eles(col)
    if eles:
        return "%s_%s" % (eles[1], eles[0])
    else:
        raise ValueError("not valid column name", col)


def is_ele(ele):
    if ele.lower() == "h":
        return True
    return ele.lower() in vice.solar_z.keys()


def extract_eles(col):
    matches = col.split("_")
    if ((len(matches) == 2)
        and is_ele(matches[0])
        and is_ele(matches[1])
        ):
        return matches
    return False


def order_abundance_ratios(df):
    """Flips abundance ratios to correspond to the order of the elements in ELEMENTS"""
    cols = df.keys()
    ele_cols = ele_columns()

    for col in ele_cols:
        col2 = invert_name(col)
        if col not in cols:
            if col2 in cols:
                df[col] = -df[col2]
                df.drop(col2, axis=1, inplace=True)
            else:
                print("warning, no data for ", col)
    return df


def drop_z_cols(df):
    """Removes abundance columns from the dataframe inplace (in the form z(x))"""
    for col in df.keys():
        if is_z_col(col):
            df.drop(col, axis=1, inplace=True)

def is_z_col(col):
    """is the column in vice's z(x) abundance format"""
    r = re.compile(r"z\([a-z]{1,2}\)")
    return r.match(col)


def rename_columns(df):
    """Renames the abundance-ratio columns of the dataframe to be in
    apogee-like format"""
    new_cols = []
    for col in df.keys():
        if is_abund_ratio(col):
            new_col = new_name(col)
        else:
            new_col = col

        new_cols.append(new_col)

    df.columns = new_cols
    return df
    
def is_abund_ratio(col):
    """is the column in vice's abundance ratio format"""
    r = re.compile(r"\[[a-z]{1,2}/[a-z]{1,2}\]")
    if r.match(col):
        return True
    return False


def load_cdf():
    """Loads the CDF of radii for the subgiant sample."""
    return pd.read_csv(os.path.join(DATA_DIR, "R_subgiants_cdf.csv"))


def rand_radii(cdf, rng=np.random.default_rng()):
    """Randomly selects a radius from the CDF."""
    p = rng.uniform(0, 1)
    return cdf.R.loc[cdf.cdf > p].iloc[0]


def rand_star(stars, cdf, width, rng=np.random.default_rng()):
    """Randomly selects a star from the given stars dataframe."""
    zone = R_to_zone(rand_radii(cdf, rng=rng), width)
    return rand_star_in_zone(stars, zone, rng=rng)


def rand_star_in_zone(stars, zone, rng=np.random.default_rng()):
    """
    Randomly selects a star from the given zone, 
    returned as a single-row dataframe.
    """
    df = stars.loc[stars.zone_final == zone]

    size = len(df)
    weights = df["weight"] / np.sum(df["weight"])
    index = rng.choice(np.arange(size), p=weights)

    return df.iloc[index:index+1]

    




def get_analytic_migration_ini_fin(filename):
    """
    get_analytic_migration_ini_fin(filename)

    Returns the R, z, initial, and final radii of stars
    from the analytic_migration_2d class.
    """

    df = pd.read_csv(filename)
    return df


def calculate_z(output):
    """
    Calculate the absolute z height of the stars in a VICE hydrodiskstars output.
    """
    analog_data = load_analogdata(output.name + "_star_migration.dat")
    return [np.abs(row[-1]) for row in analog_data][:output.stars.size[0]]


def load_analogdata(filename):
    """
    Load the analogdata file from a VICE hydrodiskstars output.
    """
    # from VICE/src/utils
    # last column of analogdata is z_height_final
    data = []
    with open(filename, 'r') as f:
        line = f.readline()
        while line[0] == '#':
            line = f.readline()
        while line != '':
            line = line.split()
            data.append([int(line[0]), float(line[1]), float(line[-1])])
            line = f.readline()
        f.close()
    return data


