import pytest
from pytest import approx

from surp import gce_math as gcem
import numpy as np


def test_Z_to_MH_single():
    assert gcem.Z_to_MH(0.016) == approx(0.0)

def test_MH_Z_MH():
    MH1 = np.random.uniform(-8, 2, 1000)
    Z1 = gcem.MH_to_Z(MH1)
    MH2 = gcem.Z_to_MH(Z1)

    assert MH2 == approx(MH1)
