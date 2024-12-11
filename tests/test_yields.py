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

    set_yields(y_c_cc=y)
    assert cc["c"] == y

    set_yields(y0_n_cc=y)
    assert cc["n"]== y

    set_yields(y_fe_cc=y)
    assert cc["fe"]== y

    set_yields(y0_c_cc=y, y_c_cc="BiLogLin", kwargs_c_cc={})
    assert isinstance(cc["c"], surp.yield_models.BiLogLin_CC)

    set_yields(y0_c_cc=y, y_c_cc="LogLin", kwargs_c_cc={})
    assert isinstance(cc["c"], surp.yield_models.LogLin_CC)

    set_yields(y0_c_cc=y, y_c_cc="Lin", kwargs_c_cc={})
    assert isinstance(cc["c"], surp.yield_models.Lin_CC)

    set_yields(y0_c_cc=y, y_c_cc="LogLin", kwargs_c_cc={})
    assert isinstance(cc["c"], surp.yield_models.LogLin_CC)

    set_yields(y0_c_cc=y, y_c_cc="Quadratic", kwargs_c_cc={})
    assert isinstance(cc["c"], surp.yield_models.Quadratic_CC)



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
# def test_reset_defaults():
#     yields.set_yields()
#     ccsne["o"] = 0
#     yields.set_defaults()
#     assert ccsne["o"] = 
# 
#     assert sneia["c"] =  
#     assert sneia["c"] =  



def test_scale_and_reset_yields():
    scale = 1.23

    for ele in ["c", "n", "o", "fe", "mg"]:

        set_yields(yield_scale=1)
        yc, ya, yi = surp.yields.copy_current_yields(ele)
        set_yields(yield_scale=scale)
        yc2, ya2, yi2 = surp.yields.copy_current_yields(ele)

        if callable(yc):
            Ztest = [0.001, 0.01, 0.02]
            for Z in Ztest:
                assert scale * yc(Z) == approx(yc2(Z))
        else:
            assert scale * yc == approx(yc2)

        assert scale * yi == approx(yi2)

        Ztest = [0.001, 0.01, 0.02]
        Mtest = [1, 2, 3]
        for Z in Ztest:
            for M in Mtest:
                assert scale * ya(Z, M) == approx(ya2(Z, M))

        surp.yields.reset_yields(ele, (yc, ya, yi))
        yc3, ya3, yi3 = surp.yields.copy_current_yields(ele)

        assert yc3 == yc
        assert ya3 == ya
        assert yi3 == yi



def test_calc_y():
    cc["c"] = 0.01
    agb["c"] = surp.yield_models.ZeroAGB()
    ia["c"] = 0.03

    # differences are due to finite integration for SNeIa yields
    assert surp.yields.calc_y() == approx(0.04, rel=1e-1)
    assert surp.yields.calc_y([0.01, 0.02, 0.03]) == approx(0.04, rel=1e-1)
    assert surp.yields.calc_y(kind="agb") == 0
    assert surp.yields.calc_y(kind="cc") == approx(0.01, rel=1e-9)
    assert surp.yields.calc_y(kind="ia") == approx(0.03, rel=1e-1)


    y = surp.yield_models.LogLin_CC()
    cc["ag"] = y
    Z = [0.001, 0.03, 0.01, 0.0001]

    assert np.all(surp.yields.calc_y(Z, ele="ag", kind="cc") == np.array([y(Z) for Z in Z]))


    y = surp.yield_models.C_AGB_Model(y0=0.001, zeta=-0.001)
    agb["n"] = y
    cc["n"] = 1.02
    MH = surp.gce_math.Z_to_MH(Z)
    assert surp.yields.calc_y(Z, ele="n", kind="agb") == approx(0.001 - 0.001 * MH, rel=1e-2)

def test_print_yields():
    surp.yields.print_yields()


