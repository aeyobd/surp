import pytest
from pytest import approx

from surp import gce_math as gcem
import surp
import numpy as np
import vice


def assert_are_inverses(f1, f2, x):
    y = f1(x)
    assert f2(y) == approx(x)
    assert f1(f2(y)) == approx(y) 



def test_mol_mass():
    assert gcem.molar_mass('H') == 1.0 # exact, see documentation
    assert gcem.molar_mass('c') == approx(12.0107, rel=1e-4)
    assert gcem.molar_mass('n') == approx(14.0067, rel=1e-4)
    assert gcem.molar_mass('o') == approx(15.9994, rel=1e-4)
    assert gcem.molar_mass('mg') == approx(24.305, rel=1e-4)
    assert gcem.molar_mass('fe') == approx(55.845, rel=1e-4)


def test_solar_z():
    assert gcem.solar_z('H') == 1.0
    for ele in surp.ELEMENTS:
        assert gcem.solar_z(ele) == approx(vice.solar_z(ele))



def test_Z_to_MH_single():
    assert gcem.Z_to_MH(0.016) == approx(0.0)
    assert gcem.Z_to_MH(0.0016) == approx(-1.0)
    assert gcem.Z_to_MH(0.16) == approx(1.0)
    assert gcem.Z_to_MH(0) == -np.inf


def test_MH_to_Z_single():
    assert gcem.MH_to_Z(0.0) == approx(0.016)
    assert gcem.MH_to_Z(-1.0) == approx(0.0016)
    assert gcem.MH_to_Z(1.0) == approx(0.16)
    assert gcem.MH_to_Z(-np.inf) == 0.0


def test_Z_MH_inverse():
    MH1 = np.random.uniform(-8, 2, 1000)
    assert_are_inverses(gcem.MH_to_Z, gcem.Z_to_MH, MH1)



def test_brak_to_abund():
    print(surp.ELEMENTS)
    for ele in surp.ELEMENTS:
        assert gcem.brak_to_abund(0, ele) == approx(vice.solar_z(ele))
        assert gcem.brak_to_abund(-1, ele) == approx(0.1 * vice.solar_z(ele))
        assert gcem.brak_to_abund(1, ele) == approx(10 * vice.solar_z(ele))

def test_abund_to_brak():
    for ele in surp.ELEMENTS:
        assert gcem.abund_to_brak(vice.solar_z(ele), ele) == approx(0)
        assert gcem.abund_to_brak(0.1 * vice.solar_z(ele), ele) == approx(-1)
        assert gcem.abund_to_brak(10 * vice.solar_z(ele), ele) == approx(1)


def test_brack_abund_inverse():
    abund = np.random.uniform(0.0001, 0.05, 1000)
    for ele1 in surp.ELEMENTS:
        for ele2 in surp.ELEMENTS + ["h"]:
            assert_are_inverses(lambda x: gcem.abund_to_brak(x, ele1, ele2), lambda x: gcem.brak_to_abund(x, ele1, ele2), abund)


def test_log_to_brack():
    pass


def test_log_to_abundance():
    pass


def test_eps_to_X():
    # eps to log
    # eps to brack
    # eps to abund
    # use Mag + 22 meanwhie
    surp.yields.set_mag22_scale()
    pass




def test_cpn():
    assert gcem.cpn(0, 0) == approx(0)
    assert gcem.cpn(1, 1) == approx(1)
    assert gcem.cpn(0.1, 0.25) == approx(1)


def test_cmp():
    assert gcem.cmn(0, 0) == approx(0)
    assert gcem.cmn(1, 1) == approx(0)
    pass





def test_high_alpha_cutoff():
    assert gcem.mg_fe_cutoff(0.0) == approx(0.16)
    assert gcem.mg_fe_cutoff(-1.0) == approx(0.16 + 0.13)
    assert gcem.mg_fe_cutoff(-2.0) == approx(0.16 + 0.26)
    assert gcem.mg_fe_cutoff(0.1) == approx(0.16)
    assert gcem.mg_fe_cutoff(1.23) == approx(0.16)


def test_is_high_alpha():
    # mg_fe versus fe_h
    assert gcem.is_high_alpha(0.0, 0.0) == False
    assert gcem.is_high_alpha(1.0, 0.0) == True
    assert gcem.is_high_alpha(0.2, -1.0) == False
    assert gcem.is_high_alpha(0.2, 1.0) == True

