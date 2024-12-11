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
VICE_OUT = None

PARAMS = test_create_model.PARAMS


def test_load_vice_model():
    VICE_OUT = vice.output("test.vice")

    assert isinstance(VICE_OUT, vice.multioutput)

    SURP_VICE = surp.ViceModel.from_vice("test.vice", PARAMS.zone_width)
    assert isinstance(SURP_VICE, surp.ViceModel)

