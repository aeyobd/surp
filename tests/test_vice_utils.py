import pytest
from pytest import approx

from surp import vice_utils as vu
import pandas as pd
import numpy as np



def test_new_name():
    assert vu.new_name("[c/mg]") == "C_MG"
    assert vu.new_name("[o/H]") == "O_H"


def test_invert_name():
    assert vu.invert_name("C_MG") == "MG_C"
    assert vu.invert_name("O_H") == "H_O"
    assert vu.invert_name("FE_MG") == "MG_FE"

    with pytest.raises(ValueError):
        vu.invert_name("C")

def test_ele_columns():
    cols = vu.ele_columns()
    assert "C_MG" in cols
    assert "MG_H" in cols
    assert "MG_FE" in cols


def test_is_abund_ratio():
    assert not vu.is_abund_ratio("12/34")
    assert not vu.is_abund_ratio("")
    assert not vu.is_abund_ratio("xkcd")
    assert not vu.is_abund_ratio("[asdf/]")
    assert not vu.is_abund_ratio("[asb/h]")
    assert not vu.is_abund_ratio("MG_FE")
    assert vu.is_abund_ratio("[mg/h]")
    assert vu.is_abund_ratio("[c/a]")
    assert vu.is_abund_ratio("[li/xe]")


def test_extract_eles():
    assert not vu.extract_eles("adf")
    assert not vu.extract_eles("[mg/fe]")
    assert vu.extract_eles("FE_H") == ["FE", "H"]


def test_is_ele():
    assert not vu.is_ele("")
    assert not vu.is_ele("asdf")
    assert vu.is_ele("h")
    assert vu.is_ele("HE")
    assert vu.is_ele("Xe")


def test_ssp_weight():
    assert vu.ssp_weight(1, 0, 10) == 1
    # linear scale with mass
    assert vu.ssp_weight(2.345, 0, 10) == 2.345

    # metallicity independent
    assert vu.ssp_weight(1.2, 1, 10) == 1.2
    assert vu.ssp_weight(1.2, -0.5, 10) == 1.2

    # truncated at 2Gyr
    assert vu.ssp_weight(1, 0, 1.99) == 0
    assert vu.ssp_weight(1, 0, 2.01) == 1


def test_zone_to_R():
    zone_width = 0.2

    assert vu.zone_to_R(0, zone_width) == 0.1
    assert vu.zone_to_R(5, zone_width) == 1.1
    assert vu.zone_to_R(7, zone_width) == 1.5
    
    zone_width = 0.1
    assert vu.zone_to_R(0, zone_width) == 0.05
    assert vu.zone_to_R(5, zone_width) == 0.55
    assert vu.zone_to_R(7, zone_width) == 0.75


def test_R_to_zone():
    zone_width = 0.2

    assert vu.R_to_zone(0, zone_width) == 0
    assert vu.R_to_zone(1.1, zone_width) == 5
    assert vu.R_to_zone(1.5, zone_width) == 7

def test__zone_to_int():
    assert vu._zone_to_int("zone0") == 0
    assert vu._zone_to_int("zone1") == 1
    assert vu._zone_to_int("zone10") == 10
    assert vu._zone_to_int("zone231") == 231




df_ini = pd.DataFrame(dict(
    MG_H = [0.1, 0.2, 0.3],
    MG_C = [0.4, 0.22, 0.0],
    FE_H = [0.5, 0.6, 0.2],
        ))

STARS = pd.DataFrame(dict(
    id = [1, 2, 3, 4, 5],
    zone_final = [0,0,1,1, 2],
    weight = [2, 1, 3, 3.5, 0.23],
    MG_H = [0.1, 0.2, 0.3, 0.4, 0.5],
    C_MG = [0.4, 0.22, 0.0, 0.1, -0.2],
    FE_H = [0.5, 0.6, 0.2, 0.3, 0.4],
    MG_FE = [-0.4, -0.4, -0.1, -0.1, -0.1],
    ))

# integration type tests
def test_order_abundance_ratios():
    df = df_ini.copy()
    df = vu.order_abundance_ratios(df)
    assert "C_MG" in df.columns
    assert "MG_H" in df.columns
    assert "FE_H" in df.columns

def test_rand_star_in_zone():
    df0 = pd.DataFrame()
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    for i in range(1000):
        s = vu.rand_star_in_zone(STARS, 0)
        df0 = pd.concat([df0, s], ignore_index=True)
        s = vu.rand_star_in_zone(STARS, 1)
        df1 = pd.concat([df1, s], ignore_index=True)
        s = vu.rand_star_in_zone(STARS, 2)
        df2 = pd.concat([df2, s], ignore_index=True)

    assert df0["zone_final"].unique() == [0]
    assert np.sum(df0.id == 1) > 611 # ~ 5sigma
    assert np.sum(df0.id == 2) > 279

    assert df1["zone_final"].unique() == [1]
    assert np.sum(df1.id == 3) > 403
    assert np.sum(df1.id == 4) > 480

    assert df2["zone_final"].unique() == [2]
    assert np.all(df2.id == 5)


def test_create_star_sample():
    zone_width = 1.5
    cdf = pd.DataFrame(dict(
        R = [0.75, 1.4, 2.75, 4.0],
        cdf = [0.0, 0.1, 0.8, 1.0]
        ))
    df = vu.create_star_sample(STARS, cdf, 1000, zone_width)
    print(df.zone_final.value_counts())
    assert len(df) == 1000
    assert np.all(np.isin(df.zone_final, [0, 1, 2]))

    expected_counts = np.array([0.1, 0.7, 0.2]) * 1000
    observed_counts = [np.sum(df.zone_final == i) for i in [0, 1, 2]]

    chi2 = np.sum((observed_counts - expected_counts)**2 / expected_counts)
    assert chi2 < 21.1 # 99.99% confidence band
    assert chi2 > 0.00521


    # check that properties are the same as in STARS
    for col in ["MG_H", "C_MG", "FE_H", "MG_FE"]:
        assert np.all(df[col + "_true"] == STARS[col].values[df.id - 1])

    # check errors
    assert df["MG_H_err"].values == approx(vu.mg_h_err(df["FE_H_true"]).values)
    assert df["C_MG_err"].values == approx(vu.c_mg_err(df["FE_H_true"]).values)
    assert df["MG_FE_err"].values == approx(vu.mg_fe_err(df["FE_H_true"]).values)

    x = (df["MG_H"] - df["MG_H_true"]) / df["MG_H_err"]
    assert np.all(np.abs(x) < 5)
    assert np.mean(x) == approx(0, abs=0.1)
    assert np.std(x) == approx(1, abs=0.1)
