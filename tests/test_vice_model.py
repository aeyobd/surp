# depends on create model, will fail otherwise....

import os
import pytest
from pytest import approx
import numpy as np 
import vice
import surp
from surp import vice_utils as vu

import sys
sys.path.append(".")
import test_create_model


SURP_VICE = None
SURP_VICE2 = None
VICE_OUT = None
VICE_OUT2 = None

PARAMS = test_create_model.PARAMS


def test_load_vice_model():
    global SURP_VICE, SURP_VICE2, VICE_OUT, VICE_OUT2
    VICE_OUT = vice.output("test.vice")

    assert isinstance(VICE_OUT, vice.multioutput)
    SURP_VICE = surp.ViceModel.from_vice("test.vice", PARAMS.zone_width, num_stars=1_000, migration_data="analytic")
    assert isinstance(SURP_VICE, surp.ViceModel)
    assert len(SURP_VICE.stars) == 1_000

    VICE_OUT2 = vice.output("test2.vice")
    assert isinstance(VICE_OUT2, vice.multioutput)

    SURP_VICE2 = surp.ViceModel.from_vice("test2.vice", PARAMS.zone_width, hydrodisk=True, num_stars=300, migration_data="hydrodisk")
    assert isinstance(SURP_VICE2, surp.ViceModel)
    assert len(SURP_VICE2.stars) == 300


def test_history_consistency():
    for out, model in [(VICE_OUT, SURP_VICE), (VICE_OUT2, SURP_VICE2)]:
        for zone in range(len(out.zones.keys())):
            h = out.zones["zone%d" % zone].history
            h2 = model.history[model.history.zone == zone]
            assert len(h["time"]) == len(h2)

            for key in ["time", "sfr", "ifr", "eta_0", "mgas", "mstar", "r_eff"]:
                assert h[key] == approx(h2[key].values, nan_ok=True)

            assert h["[c/h]"] == approx(h2["C_H"].values, nan_ok=True)
            assert h["[mg/h]"] == approx(h2["MG_H"].values, nan_ok=True)
            assert h["[m/h]"] == approx(h2["M_H"].values, nan_ok=True)
            assert h["[mg/fe]"] == approx(h2["MG_FE"].values, nan_ok=True)

def test_stars_unsampled():
    for out, model in [(VICE_OUT, SURP_VICE), (VICE_OUT2, SURP_VICE2)]:
        s = out.stars
        s2 = model.stars_unsampled

        assert len(s["zone_final"]) == len(s2)

        for key in ["mass", "age", "zone_origin", "zone_final", "z"]:
            assert s[key] == approx(s2[key].values, nan_ok=True)

        assert s["[c/h]"] == approx(s2["C_H"].values, nan_ok=True)
        assert s["[mg/h]"] == approx(s2["MG_H"].values, nan_ok=True)
        assert s["[m/h]"] == approx(s2["M_H"].values, nan_ok=True)
        assert s["[mg/fe]"] == approx(s2["MG_FE"].values, nan_ok=True)
        assert s["zone_origin"] == approx(vu.R_to_zone(s2["r_origin"].values, model.zone_width))
        assert s["zone_final"] == approx(vu.R_to_zone(s2["r_final"].values, model.zone_width))


def test_save_reload():
    SURP_VICE.save("test.json", overwrite=True)
    SURP_VICE2.save("test2.json", overwrite=True)
    s = surp.ViceModel.from_file("test.json")
    s2 = surp.ViceModel.from_file("test2.json")

    assert isinstance(s, surp.ViceModel)
    assert isinstance(s2, surp.ViceModel)
        
    for col in s.history.columns:
        assert s.history[col].values == approx(SURP_VICE.history[col].values, nan_ok=True)
        assert s2.history[col].values == approx(SURP_VICE2.history[col], nan_ok=True)

    for col in s.stars_unsampled.columns:
        assert s.stars_unsampled[col].values == approx(SURP_VICE.stars_unsampled[col].values, nan_ok=True)
        assert s2.stars_unsampled[col].values == approx(SURP_VICE2.stars_unsampled[col].values, nan_ok=True)
    for col in s.stars.columns:
        assert s.stars[col].values == approx(SURP_VICE.stars[col].values, nan_ok=True)
        assert s2.stars[col].values == approx(SURP_VICE2.stars[col].values, nan_ok=True)



