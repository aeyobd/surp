import pytest
from pytest import approx

import numpy as np

from surp.agb_interpolator import interpolator
from surp import gce_math as gcem
import surp

import vice


def are_equal(a, b, m_min=1.3):
    M = np.random.uniform(m_min, 8, 1000)
    Z = np.random.uniform(0, 0.03, 1000)

    y1 = [a(M[i], Z[i]) for i in range(1000)]
    y2 = [b(M[i], Z[i]) for i in range(1000)]
    assert y1 == approx(y2)


def assert_grid_points(a, b):
    assert a.masses == approx(b.masses)
    assert a.metallicities == approx(b.metallicities)

    ya = [a(M, Z) for M in a.masses for Z in a.metallicities]
    yb = [b(M, Z) for M in b.masses for Z in b.metallicities]
    assert np.array(ya) == approx(np.array(yb))


def test_vanilla():
    a = interpolator("c")
    b = vice.yields.agb.interpolator("c")
    are_equal(a, b)


def test_studies():
    for study in surp.AGB_MODELS:
        a = interpolator("c", study=study)
        b = vice.yields.agb.interpolator("c", study=study)
        are_equal(a, b, m_min=1.5)


def test_scaling():
    a = interpolator("c")
    scale = 0.1234
    b = a * scale

    M = np.random.uniform(0.08, 8, 1000)
    Z = np.random.uniform(0, 0.03, 1000)

    y1 = [scale * a(M[i], Z[i]) for i in range(1000)]
    y2 = [ b(M[i], Z[i]) for i in range(1000)]
    assert y1 == approx(y2)


    a = interpolator("c")
    scale = 0.1234
    b = a.copy()
    b *= scale

    M = np.random.uniform(0.08, 8, 1000)
    Z = np.random.uniform(0, 0.03, 1000)

    y1 = [scale * a(M[i], Z[i]) for i in range(1000)]
    y2 = [ b(M[i], Z[i]) for i in range(1000)]
    assert y1 == approx(y2)


    a = interpolator("c")
    scale = 0.243
    b = interpolator("c", prefactor=scale)

    M = np.random.uniform(0.08, 8, 1000)
    Z = np.random.uniform(0, 0.03, 1000)

    y1 = [scale * a(M[i], Z[i]) for i in range(1000)]
    y2 = [ b(M[i], Z[i]) for i in range(1000)]
    assert y1 == approx(y2)


def test_mass_factor():
    a = interpolator("c")
    scale = 0.256
    b = interpolator("c", mass_factor=scale)
    M = np.linspace(0.05, 8.23, 1000)
    Z = np.random.uniform(0, 0.03, 1000)

    y2 = [b(M[i]*scale, Z[i]) for i in range(1000)]
    assert [a(M[i], Z[i]) for i in range(1000)] == approx(y2)

    a = interpolator("c")
    scale = 1.31
    b = interpolator("c", mass_factor=scale)
    M = np.linspace(0.05, 7.99, 1000)

    y2 = [b(M[i], Z[i]) for i in range(1000)]
    assert [a(M[i] / scale, Z[i]) for i in range(1000)] == approx(y2)

    assert b(8.1, 0.01) == approx(0)

def test_truncate():
    pass


def test_pinch():
    a = interpolator("c")


def test_attributes():
    a = interpolator("c", pinch_mass=None)
    y, m, z = vice.yields.agb.grid("c")
    assert np.array(a.yields) == approx(np.array(y))
    assert a.masses == approx(m)
    assert a.metallicities == approx(z)



def test_low_z_flat():
    a = interpolator("c")
    zl = a.metallicities[0]
    zll = zl / 2
    Ms = np.random.uniform(1.3, 8, 1000)

    a = np.vectorize(a)

    assert a(Ms, zl) != approx(a(Ms, zll))

    b = interpolator("c", low_z_flat=True)
    b = np.vectorize(b)
    assert b(Ms, zl) == approx(b(Ms, zll))


def test_log_interp():
    a = interpolator("c")
    b = interpolator("c", interp_kind="log")
    assert_grid_points(a, b)

def test_spline():
    a = interpolator("c")
    b = interpolator("c", interp_kind="spline")
    assert_grid_points(a, b)

    
