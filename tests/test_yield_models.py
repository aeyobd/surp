import pytest
from pytest import approx

import numpy as np

from surp.yield_models import LinAGB, ZeroAGB, C_AGB_Model, C_CC_Model
from surp.analysis import gce_math as gcem



def model_rscales(model, M, Z, factor=0.1234):
    yagb = model
    yagb1 = yagb*factor
    return yagb(M, Z)*factor == approx(yagb1(M, Z))

def model_lscales(model, M, Z, factor=0.1234):
    yagb = model
    yagb1 = factor * yagb
    return yagb(M, Z)*factor == approx(yagb1(M, Z))

def model_iscales(model, M, Z, factor=0.1234):
    yagb = model
    yagb1 = yagb.copy()
    yagb1 *= factor
    return yagb(M, Z)*factor == approx(yagb1(M, Z))


@pytest.fixture
def zero_agb():
    return ZeroAGB()

N = 1000
@pytest.fixture
def Ms():
    return np.random.uniform(0.08, 8, N)

@pytest.fixture
def Zs():
    MHs = np.random.uniform(-4, 1, N)
    Zs = gcem.MH_to_Z(MHs)
    return Zs

def test_zero_agb_val(zero_agb, Ms, Zs):
    assert zero_agb(Ms, Zs) == 0


def test_zero_agb_scale(zero_agb, Ms, Zs):
    model = zero_agb
    assert model_rscales(model, Ms, Zs)
    assert model_lscales(model, Ms, Zs)
    assert model_iscales(model, Ms, Zs)



def test_zero_agb_str(zero_agb):
    assert str(zero_agb) == "0"


def test_lin_agb_val(Ms, Zs):
    eta = 0.5
    y0 = 0.01
    yagb = LinAGB(eta=eta, y0=y0)
    expected = Ms*(y0 + Zs/gcem.Z_SUN*eta)
    assert yagb(Ms, Zs) == approx(expected)

def test_lin_agb_val(Ms, Zs):
    eta = 0.5
    yagb = LinAGB(eta=eta)
    expected = Ms*(Zs/gcem.Z_SUN*eta)
    assert yagb(Ms, Zs) == approx(expected)


def test_lin_agb_scale(Ms, Zs):
    model = LinAGB(0.5, 0.01)
    assert model_rscales(model, Ms, Zs)
    assert model_lscales(model, Ms, Zs)
    assert model_iscales(model, Ms, Zs)


def test_lin_agb_str():
    model = LinAGB(eta=0.2, y0=0.08)
    expected = "8.00e-02 M + 2.00e-01 M Z/Z0"
    assert str(model) == expected

    model = LinAGB(eta=0.12)
    expected = "1.20e-01 M Z/Z0"
    assert str(model) == expected


def test_lin_agb_nonreal():
    lin_agb = LinAGB(eta=0.12, y0=-0.1)
    with pytest.raises(TypeError):
        lin_agb * "nonreal number"
    with pytest.raises(TypeError):
        lin_agb * None




def test_CC_val(Zs):
    y0 = 0.003
    zeta = 0.13
    expected = y0 + zeta*(Zs-gcem.Z_SUN)
    model = C_CC_Model(y0, zeta=zeta)
    assert model(Zs) == approx(expected)

def test_CC_lowz(Zs):
    y0 = 0.003
    zeta = 0.13
    zl = 0.007
    yl = 0
    y2 = y0 + zeta*(zl - gcem.Z_SUN)
    zetal = y2/zl

    model = C_CC_Model(y0, zeta=zeta, yl=yl, zl=zl)

    Zs = np.random.uniform(zl, 0.01, 1000)
    expected = y0 + zeta*(Zs-gcem.Z_SUN)
    assert model(Zs) == approx(expected)

    Zs = np.random.uniform(0, zl, 1000)
    expected = yl + zetal*Zs
    assert model(Zs) == approx(expected)


def test_cc_nonreal():
    model = C_CC_Model(0.123, 0.042)
    with pytest.raises(TypeError):
        model * "nonreal number"
    with pytest.raises(TypeError):
        None * model
