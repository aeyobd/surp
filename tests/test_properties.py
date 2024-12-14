
import pytest 
from pytest import approx
import surp
import surp.simulation.properties as sp

import sys
sys.path.append(".")
from test_create_model import PARAMS, PARAMS2

import vice


MODEL = surp.simulation.create_model(PARAMS)
MODEL2 = surp.simulation.create_model(PARAMS2)

def test_migration():
    migration = MODEL.migration.stars


def test_sf_law():
    for i in range(len(MODEL.zones)):
        zone = MODEL.zones[i]
        assert isinstance(zone.tau_star, vice.toolkit.J21_sf_law)
    ts0 = MODEL.zones[0].tau_star

    # mol when 2.0e+07 < Sigma gas, so want 
    # TODO: should work for 13.2.........
    assert ts0(12.2, 1) == approx(PARAMS.tau_star0)

    for zone in MODEL2.zones:
        assert isinstance(zone.tau_star, sp.twoinfall_sf_law)
        params = PARAMS2

        assert zone.tau_star.nu1 == params.sfh_kwargs["nu1"]
        assert zone.tau_star.nu2 == params.sfh_kwargs["nu2"]
        assert zone.tau_star.t2 == params.sfh_kwargs["t2"]

