
import pytest
from pytest import approx

import numpy as np

import surp.utils as utils



def test_get_bin_number():
    bins = [0, 1, 2, 3, 4, 5]
    assert utils.get_bin_number(bins, 0) == 0
    assert utils.get_bin_number(bins, 1.2) == 1

    assert utils.get_bin_number(bins, -0.000001) == -1
    assert utils.get_bin_number(bins, 5.000001) == -1


def test_interpolate():

    x1, y1 = 0, 0
    x2, y2 = 1, 1

    a = np.random.rand(100)
    assert utils.interpolate(x1, y1, x2, y2, a) == approx(a)


    x1, y1 = 0, 0
    x2, y2 = 1, 2.5

    assert utils.interpolate(x1, y1, x2, y2, a) == approx(2.5*a)


    x1, y1 = 1, 0
    x2, y2 = 0, 1.5

    assert utils.interpolate(x1, y1, x2, y2, a) == approx(1.5 - 1.5*a)


def test_is_real():

    @utils.arg_isreal()
    def f(x):
        return x

    assert f(1) == 1
    assert f(1.0) == 1.0

    # errors
    with pytest.raises(TypeError):
        f(1j)
    with pytest.raises(TypeError):
        f("hi")
    with pytest.raises(TypeError):
        f(None)

def test_numpylike():
    @utils.arg_numpylike()
    def f(x):
        return x


    assert f([1,2]) == approx(np.array([1,2]))
    assert isinstance(f([1,2]), np.ndarray)
    assert isinstance(f((1,2)), np.ndarray)
    assert isinstance(f(np.array([1,2])), np.ndarray)
