import pytest

from surp import vice_utils as vu



def test_new_name():
    assert vu.new_name("[c/mg]") == "C_MG"
    assert vu.new_name("[o/H]") == "O_H"

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
