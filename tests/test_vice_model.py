# depends on create model, will fail otherwise....

import os
import pytest
from pytest import approx
import numpy as np 
import vice
import surp

import sys
sys.path.append(".")
import test_create_model


SURP_VICE = None
SURP_VICE2 = None
VICE_OUT = None
VICE_OUT2 = None

PARAMS = test_create_model.PARAMS


def test_load_vice_model():
    VICE_OUT = vice.output("test.vice")

    assert isinstance(VICE_OUT, vice.multioutput)
    SURP_VICE = surp.ViceModel.from_vice("test.vice", PARAMS.zone_width, num_stars=1_000)
    assert isinstance(SURP_VICE, surp.ViceModel)
    assert len(SURP_VICE.stars) == 1_000

    VICE_OUT2 = vice.output("test2.vice")
    assert isinstance(VICE_OUT2, vice.multioutput)

    # TODO: cannot find analog_data.dat
    SURP_VICE2 = surp.ViceModel.from_vice("test2.vice", PARAMS.zone_width, hydrodisk=True, num_stars=300)
    assert isinstance(SURP_VICE2, surp.ViceModel)
    assert len(SURP_VICE2.stars) == 300


def test_history_consistency():
    pass


def test_stars_unsampled():
    # check columns and correspondance
    pass


def test_stars_cdf():
    pass

def test_stars_err():
    pass


def test_save_reload():
    pass


