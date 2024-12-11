import pytest
from pytest import approx
import surp
import vice
import numpy as np
from scipy.integrate import quad

import surp.simulation.sfh_models as sfh_models


Nt = 100

@pytest.fixture
def times():
    return np.append(np.logspace(-2, np.log(13.2), Nt-1), 0.)



def test_static(times):
    sfh = sfh_models.static()

    expected = [1.] * Nt
    assert [sfh(t) for t in times] == approx(expected)

    sfh.norm = 1.5
    assert [sfh(t) for t in times] == approx([1.5*i for i in expected])


def test_insideout(times):
    sfh = sfh_models.insideout(tau_rise=2.5, tau_sfh=6.0)

    expected = np.exp(-times / 6) * (1 - np.exp(-times / 2.5))
    assert [sfh(t) for t in times] == approx(expected)
    sfh.norm = 1.5
    assert [sfh(t) for t in times] == approx(1.5 * expected)

    sfh = sfh_models.insideout(tau_rise=7, tau_sfh=3)

    expected = np.exp(-times / 3) * (1 - np.exp(-times / 7))
    assert [sfh(t) for t in times] == approx(expected)

    assert sfh(1e100) == approx(0)
    assert sfh(0) == 0



def test_lateburst(times):
    burst_size = 1.1
    burst_width= 0.5
    burst_time = 10
    tau_rise = 2.2
    tau_sfh = 6.5
    sfh = sfh_models.lateburst(
        burst_size=burst_size, burst_width=burst_width, burst_time=burst_time,
        tau_rise=tau_rise, tau_sfh=tau_sfh
    )

    expected = np.exp(-times / tau_sfh) * (1 - np.exp(-times / tau_rise))
    expected *= (1 + burst_size * np.exp(-(times - burst_time)**2 / (2*burst_width**2)))

    assert [sfh(t) for t in times] == approx(expected)
    assert sfh(1e100) == approx(0)
    assert sfh(0) == 0

    sfh.norm = 0.93
    assert [sfh(t) for t in times] == approx(0.93 * expected)


def test_exp(times):
    for tau in [1, 6, 25]:
        sfh = sfh_models.exp_sfh(tau_sfh=tau)
        expected = np.exp(-times / tau) 
        assert sfh(0) == 1
        assert [sfh(t) for t in times] == approx(expected)

        sfh.norm = 0.93
        assert [sfh(t) for t in times] == approx(0.93 * expected)

    assert sfh(1e100) == approx(0)


def test_linexp(times):
    for tau in [1, 6, 25]:
        sfh = sfh_models.linexp(tau_sfh=tau)
        expected = np.exp(-times / tau) * times / tau
        assert [sfh(t) for t in times] == approx(expected)

    assert sfh(1e100) == approx(0)
    assert sfh(0) == 0

    sfh1 = sfh_models.linexp(tau_sfh=1)
    sfh2 = sfh_models.linexp(tau_sfh=1)
    sfh2.norm = 1.5
    assert [1.5 * sfh1(t) for t in times] == approx([sfh2(t) for t in times])
    


def test_twoexp(times):
    t1 = 0.1
    t2 = 3.5
    tau1 = 1.5
    tau2 = 4.0
    A2 = 0.7
    tend = 13.2

    sfh = sfh_models.twoexp(tau1=tau1, tau2=tau2, t1=t1, t2=t2, A2=A2, tend=tend)
    A = 1 / quad(lambda t: np.exp(-(t - t1) / tau1), t1, tend)[0]
    B = 1 / quad(lambda t: np.exp(-(t - t2) / tau2), t2, tend)[0]
    B *= A2

    assert sfh.A == approx(A)
    assert sfh.B == approx(B)

    expected = A * np.exp(-(times - t1) / tau1) * (t1 < times)  + B * np.exp(-(times - t2) / tau2) * (t2 < times)
    assert [sfh(t) for t in times] == approx(expected)

    sfh.norm = 1.22
    assert [sfh(t) for t in times] == approx(1.22 * expected)


def test_threeexp(times):
    t1 = 0.1
    t2 = 3.5
    t3 = 10
    tau1 = 1.5
    tau2 = 4.0
    tau3 = 0.5
    A2 = 0.7
    A3 = 0.3
    tend = 13.2

    sfh = sfh_models.threeexp(tau1=tau1, tau2=tau2, tau3=tau3, t1=t1, t2=t2, t3=t3, A2=A2, A3=A3, tend=tend)
    A = 1 / quad(lambda t: np.exp(-(t - t1) / tau1), t1, tend)[0]
    B = 1 / quad(lambda t: np.exp(-(t - t2) / tau2), t2, tend)[0]
    C = 1 / quad(lambda t: np.exp(-(t - t3) / tau3), t3, tend)[0]
    B *= A2
    C *= A3

    assert sfh.A == approx(A)
    assert sfh.B == approx(B)
    assert sfh.C == approx(C)

    expected = (A * np.exp(-(times - t1) / tau1) * (t1 < times)  
                + B * np.exp(-(times - t2) / tau2) * (t2 < times) 
                + C * np.exp(-(times - t3) / tau3) * (t3 < times))

    assert [sfh(t) for t in times] == approx(expected)

    sfh.norm = 1.22

    assert [sfh(t) for t in times] == approx(1.22 * expected)
