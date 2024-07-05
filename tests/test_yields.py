import pytest
from pytest import approx

import numpy as np
import vice

from vice.yields.agb import settings as agb
from vice.yields.ccsne import settings as cc
from vice.yields.sneia import settings as ia
from vice import solar_z

from surp.yields import YieldParams
import surp

import os

DIR = os.path.dirname(os.path.abspath(__file__))
fname = f"{DIR}/yield_params_test.toml"


def set_yields(**kwargs):
    params = YieldParams.from_file(fname, **kwargs)
    print(kwargs)
    print(params)
    surp.set_yields(params, verbose=False)


def test_default_yields():
    surp.yields.set_defaults()
    assert ia["c"] == 0
    assert ia["o"] == 0
    assert ia["mg"] == 0
    assert type(agb["o"]) == surp.yield_models.ZeroAGB

def test_load_defaults():
    set_yields()



def test_cc_set_retrieve():
    y = 1.259357 # unrealistic but will never be an actual value
    for ele in ["c", "n", "fe"]:
        print(ele)
        params = {
            f"y_{ele}_cc": y
        }

        set_yields(**params)
        assert cc[ele] == y


def test_ia_set_retrieve():
    y = 1.2321 # unrealistic but will never be an actual value
    for ele in ["c", "fe"]:
        print(ele)
        params = {
            f"y_{ele}_ia": y
        }

        set_yields(**params)
        assert ia[ele] == y

# def test_mag22():
#     assert solar_z["c"] = 
#     assert solar_z["n"] = 
#     assert solar_z["o"] = 
#     assert solar_z["fe"] = 
#     assert solar_z["mg"] = 
# 
# def test_default_settings():
#     yields.set_yields()
#     assert ccsne["o"] = 
# 
#     assert sneia["c"] =  
#     assert sneia["c"] =  
# 
# def test_reset_defaults():
#     yields.set_yields()
#     ccsne["o"] = 0
#     yields.set_defaults()
#     assert ccsne["o"] = 
# 
#     assert sneia["c"] =  
#     assert sneia["c"] =  




def test_yields_addition():
    pass


def test_fe():
    pass


def test_eta():
    pass

def test_n():
    pass


