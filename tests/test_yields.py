import pytest
from pytest import approx

import numpy as np
import vice

from vice.yields import agb
from vice.yields import ccsne as cc
from vice.yields import sneia as ia
from vice import solar_z

from surp.yields import set_yields, YieldParams


def test_fe_ia():
    params = YieldParams(fe_ia = 1.2)
    assert ia.settings["fe"] == 1.2

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


