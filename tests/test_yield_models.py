import pytest
from pytest import approx

import numpy as np

import vice
from surp.yield_models import LinAGB, ZeroAGB, C_AGB_Model
import surp.yield_models as ym
from surp import gce_math as gcem
import surp


def mdot_emperical_larson(age, h=1e-8, postMS=0.1):
    return 1/h * (vice.mlr.larson1974(age, which="age", postMS=postMS) - 
                  vice.mlr.larson1974(age - h, which="age", postMS=postMS) )

def test_mdot_larson():
    ages = np.linspace(0.08, 100, 100)
    postMS = 0.0
    expected = [mdot_emperical_larson(age, postMS=postMS) for age in ages]
    actual = [ym.mdot_larson1974(age, postMS=postMS) for age in ages]
    assert actual == approx(expected, rel=1e-4)
    postMS = 0.1
    expected = [mdot_emperical_larson(age, postMS=postMS) for age in ages]
    actual = [ym.mdot_larson1974(age, postMS=postMS) for age in ages]
    assert actual == approx(expected, rel=1e-4)

def model_rscales(model, Ms, Zs, factor=0.1234):
    yagb = model
    yagb1 = yagb*factor
    expected = [yagb(M, Z)*factor for M, Z in zip(Ms, Zs)]
    actual = [yagb1(M, Z) for M, Z in zip(Ms, Zs)]
    return actual == approx(expected)


def model_lscales(model, Ms, Zs, factor=0.1234):
    yagb = model
    yagb1 = factor * yagb

    expected = [yagb(M, Z)*factor for M, Z in zip(Ms, Zs)]
    actual = [yagb1(M, Z) for M, Z in zip(Ms, Zs)]

    return actual == approx(expected)


def model_iscales(model, Ms, Zs, factor=0.1234):
    yagb = model
    yagb1 = yagb.copy()
    yagb1 *= factor

    expected = [yagb(M, Z)*factor for M, Z in zip(Ms, Zs)]
    actual = [yagb1(M, Z) for M, Z in zip(Ms, Zs)]
    return actual == approx(expected)


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

@pytest.fixture
def y0s():
    return np.random.uniform(0.001, 0.01, N)

@pytest.fixture
def zetas():
    return np.random.uniform(-0.01, 0.01, N)



def test_zero_agb_val(zero_agb, Ms, Zs):
    assert zero_agb(Ms, Zs) == 0


def test_zero_agb_scale(zero_agb, Ms, Zs):
    model = zero_agb
    assert model_rscales(model, Ms, Zs)
    assert model_lscales(model, Ms, Zs)
    assert model_iscales(model, Ms, Zs)



def test_zero_agb_str(zero_agb):
    assert str(zero_agb) == "0"



# ===================== Lin AGB =====================
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
    actual = [yagb(M, Z) for M, Z in zip(Ms, Zs)]
    assert actual == approx(expected)


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


# ===================== C AGB =====================


def test_c_agb_integrated():
    y0 = 0.003
    zeta = -0.001
    model = ym.C_AGB_Model(y0=y0, zeta=zeta)
    Zs = [1e-6, 1e-4, 1e-3, 2e-3, 1e-2, 2e-2]

    expected = y0 + zeta * gcem.Z_to_MH(Zs)
    vice.yields.agb.settings["c"] = model
    actual = surp.yields.calc_y(Zs, kind="agb", t_end=15)
    assert actual == approx(expected, rel=3e-2)


def test_c_agb_dtd_gamma0(Zs):
    tau_agb = 2
    t_D = 0.15
    t_D = max(t_D, 0.04683040043038564) # 8 solar mass
    gamma = 0
    m_low = 0.08

    model = ym.C_AGB_Model(y0=0.003, zeta=0, 
        tau_agb=tau_agb, t_D=t_D, gamma=gamma, m_low=m_low)

    t_max = vice.mlr.larson1974(m_low)
    vice.yields.agb.settings["c"] = model
    vice.yields.ccsne.settings["c"] = 0
    vice.yields.sneia.settings["c"] = 0

    actual, times = vice.single_stellar_population("c", Z=gcem.Z_SUN, mstar=1, time=10, dt=0.001)
    skip = 30
    actual = actual[skip:]
    times = times[skip:]


    def R_int_0(t):
        ta = tau_agb
        if t > t_max - t_D:
            return R_int_0(t_max - t_D)
        if t < 0:
            return 0

        return 1/ta * (1 - np.exp(-t/ta)) 

    expected = [R_int_0(t - t_D) for t in times]
    scale =  actual[-1]/expected[-1]
    expected = [scale * R  for R in expected]

    assert actual == approx(expected, abs=1e-4)

def test_c_agb_dtd_gamma2(Zs):
    tau_agb = 1.2
    t_D = 0.25
    t_D = max(t_D, 0.04683040043038564) # 8 solar mass
    gamma = 2
    m_low = 0.08

    model = ym.C_AGB_Model(y0=0.003, zeta=0, 
        tau_agb=tau_agb, t_D=t_D, gamma=gamma, m_low=m_low)

    t_max = vice.mlr.larson1974(m_low)
    vice.yields.agb.settings["c"] = model
    vice.yields.ccsne.settings["c"] = 0
    vice.yields.sneia.settings["c"] = 0

    actual, times = vice.single_stellar_population("c", Z=gcem.Z_SUN, mstar=1, time=10, dt=0.001)
    skip = 30
    actual = actual[skip:]
    times = times[skip:]


    def R_int(t):
        x = np.array(t) 
        ta = tau_agb
        return 1/ta * (2 - ( (x/ta)**2 + 2*(x/ta) + 2) * np.exp(-x/ta)) * (t > 0) * (t < t_max)

    expected = [R_int(t - t_D) for t in times]
    scale =  actual[-1]/expected[-1]
    expected = [scale * R  for R in expected]

    assert actual == approx(expected, abs=1e-4)

# ===================== CCSNe =====================
def test_zeta_to_slope():
    zeta = 0.0562
    slope = ym.zeta_to_slope(zeta)

    Z1 = gcem.Z_SUN
    h = 1e-8*Z1
    Z2 = Z1 + h

    model = ym.Lin_CC(0.003, zeta=zeta)
    dy = model(Z2) - model(Z1)
    dlogZ = np.log10(Z2) - np.log10(Z1)

    assert dy/dlogZ == approx(zeta)
    assert dy/h == approx(slope)


# ===================== LinCC =====================
def test_Lin_CC_val(Zs):
    y0 = 0.003
    zeta = 0.13
    slope = ym.zeta_to_slope(zeta)

    expected = y0 + slope*(Zs-gcem.Z_SUN)
    model = ym.Lin_CC(y0, zeta=zeta)
    actual = [model(Z) for Z in Zs]

    assert model.slope == approx(slope)
    assert actual == approx(expected)




def test_cc_nonreal():
    model = ym.Lin_CC(0.123, 0.042)
    with pytest.raises(TypeError):
        model * "nonreal number"
    with pytest.raises(TypeError):
        None * model


# ===================== BiLinCC =====================

def test_BiLin_CC_lowz():
    y0 = 0.003
    zeta = 0.13
    zl = 0.007
    yl = 0.001

    slope = ym.zeta_to_slope(zeta)
    y2 = y0 + slope*(zl - gcem.Z_SUN)
    zetal = y2/zl

    model = ym.BiLin_CC(y0, zeta=zeta, y1=yl, Z1=zl)

    Zs = np.random.uniform(zl, 0.02, 1000)
    expected = y0 + slope*(Zs-gcem.Z_SUN)
    actual = [model(Z) for Z in Zs]
    assert actual == approx(expected)

    Zs = np.random.uniform(0, zl, 1000)
    expected = yl + (y2-yl)/zl*Zs
    actual = [model(Z) for Z in Zs]
    assert actual == approx(expected) # Broken

def test_BiLin_CC_scale(Zs):
    model = ym.BiLin_CC(0.003, 0.13, y1=0.001, Z1=0.007)

    scale = 3.14
    model2 = scale * model

    expected = [model(Z)*scale for Z in Zs]
    actual = [model2(Z) for Z in Zs]
    assert actual == approx(expected)


# ===================== LogLinCC =====================


def test_LogLin_CC_val(Zs):
    y0 = 0.00121
    zeta = -0.00011
    model = ym.LogLin_CC(y0, zeta)

    MH = gcem.Z_to_MH(Zs)

    expected = y0 + zeta*MH
    actual = np.array([model(Z) for Z in Zs])
    assert actual == approx(expected)

def test_LogLin_CC_scale(Zs):
    model = ym.LogLin_CC(0.00121, -0.00011)
    scale = 3.14
    model2 = scale * model

    expected = [model(Z)*scale for Z in Zs]
    actual = [model2(Z) for Z in Zs]
    assert actual == approx(expected)

# ===================== BiLogLinCC =====================

def test_BiLogLin_CC_val(Zs):
    y0 = 0.00121
    zeta = -0.00011
    y1 = 0.0001
    model = ym.BiLogLin_CC(y0, zeta, y1=y1)
    MH = gcem.Z_to_MH(Zs)

    expected = np.maximum(y0 + zeta*MH, y1)
    actual = np.array([model(Z) for Z in Zs])
    assert actual == approx(expected)


def test_BiLogLin_CC_scale(Zs):
    model = ym.BiLogLin_CC(0.00121, -0.00011, y1=0.0001)
    scale = 3.14
    model2 = scale * model

    expected = [model(Z)*scale for Z in Zs]
    actual = [model2(Z) for Z in Zs]
    assert actual == approx(expected)

# ===================== Piecewise_CC ===================

def test_piecewise_cc_val(Zs):
    y0s = [0.001, 0.002, -0.001]
    zetas = [0.003, 0.0077, 0.001]
    Z1s = [0.001, 0.01]

    model = ym.Piecewise_CC(y0s, zetas, Z1s)
    expected = np.zeros_like(Zs)

    MH = gcem.Z_to_MH(Zs)
    for (i, Z) in enumerate(Zs):
        if Z < Z1s[0]:
            expected[i] = y0s[0] + zetas[0]*MH[i]
        elif Z < Z1s[1]:
            expected[i] = y0s[1] + zetas[1]*MH[i]
        else:
            expected[i] = y0s[2] + zetas[2]*MH[i]

    actual = np.array([model(Z) for Z in Zs])
    assert actual == approx(expected)


def test_piecewise_cc_scale(Zs):
    y0s = [0.001, 0.002, -0.001]
    zetas = [0.003, 0.0077, 0.001]
    Z1s = [0.001, 0.01]

    model = ym.Piecewise_CC(y0s, zetas, Z1s)
    scale = 3.14
    model2 = scale * model

    expected = [model(Z)*scale for Z in Zs]
    actual = [model2(Z) for Z in Zs]
    assert actual == approx(expected)


# ===================== Quadratic =====================

def test_quad_cc_val(Zs):
    zeta = 0.022
    A = 0.012
    y0 = 0.003
    model = ym.Quadratic_CC(y0=y0, A=A, zeta=zeta)

    MH = gcem.Z_to_MH(Zs)
    expected = y0 + zeta*MH + A*MH**2
    actual = np.array([model(Z) for Z in Zs])

    vertex = -zeta/(2*A)
    expected[MH < vertex] = y0 + zeta*vertex + A*vertex**2
    assert actual == approx(expected)


    vertex = -0.5
    model = ym.Quadratic_CC(y0=y0, A=A, zeta=zeta, Z1=gcem.MH_to_Z(vertex))
    expected = y0 + zeta*MH + A*MH**2
    expected[MH < vertex] = y0 + zeta*vertex + A*vertex**2
    actual = np.array([model(Z) for Z in Zs])
    assert actual == approx(expected)


def test_quad_cc_scale(Zs):
    model = ym.Quadratic_CC(y0=0.003, A=0.012, zeta=0.022)
    scale = 3.14
    model2 = scale * model

    expected = [model(Z)*scale for Z in Zs]
    actual = [model2(Z) for Z in Zs]
    assert actual == approx(expected)
