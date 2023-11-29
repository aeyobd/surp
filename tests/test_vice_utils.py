import pytest

from surp import vice_utils as vu


def test_R_to_zone():
    pass

def zone_to_R():
    pass

def test_new_name():
    assert vu.new_name("[c/mg]") == "C_MG"
    assert vu.new_name("[o/H]") == "O_H"


def test_ele_columns():
    cols = vu.ele_columns()
    assert "C_MG" in cols

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
