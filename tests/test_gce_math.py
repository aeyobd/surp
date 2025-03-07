import pytest
from pytest import approx

from surp import gce_math as gcem
import surp
import numpy as np
import vice


ALL_ELEMS = surp.ELEMENTS + ["h"]
def assert_are_inverses(f1, f2, x):
    y = f1(x)
    assert f2(y) == approx(x)
    assert f1(f2(y)) == approx(y) 


def test_surp_elements():
    assert "c" in surp.ELEMENTS
    assert "n" in surp.ELEMENTS
    assert "mg" in surp.ELEMENTS
    assert "fe" in surp.ELEMENTS


def test_mol_mass():
    assert gcem.molar_mass('H') == approx(1.00794, rel=1e-4)
    assert gcem.molar_mass('c') == approx(12.0107, rel=1e-4)
    assert gcem.molar_mass('n') == approx(14.0067, rel=1e-4)
    assert gcem.molar_mass('o') == approx(15.9994, rel=1e-4)
    assert gcem.molar_mass('mg') == approx(24.305, rel=1e-4)
    assert gcem.molar_mass('fe') == approx(55.845, rel=1e-4)


def test_solar_z():
    assert gcem.solar_z('H') == approx(0.709)
    assert gcem.solar_z('he') == approx(0.2734)
    assert gcem.solar_z('M') == approx(0.0176)
    for ele in surp.ELEMENTS:
        assert gcem.solar_z(ele) == approx(vice.solar_z(ele))



def test_Z_to_MH_single():
    assert gcem.Z_to_MH(0.0176) == approx(0.0)
    assert gcem.Z_to_MH(0.00176) == approx(-1.0)
    assert gcem.Z_to_MH(0.176) == approx(1.0)
    assert gcem.Z_to_MH(0) == -np.inf


def test_MH_to_Z_single():
    assert gcem.MH_to_Z(0.0) == approx(0.0176)
    assert gcem.MH_to_Z(-1.0) == approx(0.0016)
    assert gcem.MH_to_Z(1.0) == approx(0.16)
    assert gcem.MH_to_Z(-np.inf) == 0.0


def test_Z_MH_inverse():
    MH1 = np.random.uniform(-8, 2, 1000)
    assert_are_inverses(gcem.MH_to_Z, gcem.Z_to_MH, MH1)



def test_brak_to_abund():
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
        assert_are_inverses(lambda x: gcem.abund_to_brak(x, ele1), lambda x: gcem.brak_to_abund(x, ele1), abund)



def test_brack_to_abund_ratio():
    for ele in ALL_ELEMS:
        for ele2 in ALL_ELEMS:
            zo = gcem.solar_z(ele) / gcem.solar_z(ele2)
            assert gcem.brak_to_abund_ratio(0, ele, ele2) == approx(zo)
            assert gcem.brak_to_abund_ratio(1, ele, ele2) == approx(10*zo)
            assert gcem.brak_to_abund_ratio(-1, ele, ele2) == approx(0.1*zo)



def test_abund_ratio_to_brack_inverses():
    x = 10 ** np.random.uniform(-2, 2, 1000)
    for ele in ALL_ELEMS:
        for ele2 in ALL_ELEMS:
            assert_are_inverses(lambda x: gcem.abund_ratio_to_brak(x, ele, ele2), lambda x: gcem.brak_to_abund_ratio(x, ele, ele2), x)



def test_log_to_brak():
    x = np.random.uniform(-2, 2, 1000)

    for (ele, ele2) in [("c", "o"), ("o", "fe"), ("c", "n")]:
        log_mu = np.log10(gcem.molar_mass(ele) / gcem.molar_mass(ele2))
        log_sun = np.log10(vice.solar_z(ele) / vice.solar_z(ele2))
        assert gcem.log_to_brak(x, ele, ele2) == approx(x + log_mu - log_sun)


def test_log_to_abundance():
    # log = log Na / Nb, so just  multiply by molar masses and 10 ^ log

    for ele in surp.ELEMENTS:
        mu = gcem.molar_mass(ele) / gcem.molar_mass("h")
        assert gcem.log_to_abundance(-1, ele) == approx(gcem.X_SUN * 0.1 * mu)
        assert gcem.log_to_abundance(-2, ele) == approx(gcem.X_SUN * 0.01 * mu)

def test_log_to_abundance_ratio():
    for ele in ALL_ELEMS:
        for ele2 in ALL_ELEMS:
            zo = gcem.molar_mass(ele) / gcem.molar_mass(ele2)
            assert gcem.log_to_abundance_ratio(0, ele, ele2) == approx(zo)
            assert gcem.log_to_abundance_ratio(1, ele, ele2) == approx(10*zo)
            assert gcem.log_to_abundance_ratio(-1, ele, ele2) == approx(0.1*zo)


def test_abundance_scale():
    # eps to log
    # eps to brack
    # eps to abund
    # use Mag + 22 meanwhie
    surp.yields.set_magg22_scale()
    correction = 0.04
    acc = 8e-3 # rounding errors. We round to 1000s place like reported
    assert surp.Z_SUN + surp.Y_SUN + surp.X_SUN == approx(1.0)
    assert surp.Z_SUN / surp.X_SUN == approx(0.0225 * 10**correction, rel=acc)


    assert gcem.eps_to_abundance(12, "h") == approx(gcem.X_SUN)
    assert gcem.eps_to_abundance(8.56 + correction, "c") == approx(vice.solar_z("c"), rel=acc)
    assert gcem.eps_to_abundance(7.98 + correction, "n") == approx(vice.solar_z("n"), rel=acc)
    assert gcem.eps_to_abundance(8.77 + correction, "o") == approx(vice.solar_z("o"), rel=acc)
    assert gcem.eps_to_abundance(7.55 + correction, "mg") == approx(vice.solar_z("mg"), rel=acc)
    assert gcem.eps_to_abundance(7.50 + correction, "fe") == approx(vice.solar_z("fe"), rel=acc)



def test_eps_to_log():
    N = 100
    eps = np.random.uniform(0, 10, N)
    for i in range(N):
        assert gcem.eps_to_log(eps[i]) == approx(eps[i] - 12)


def test_eps_to_brack():
    surp.yields.set_magg22_scale()

    correction = -0.04
    acc = 8e-3

    assert gcem.eps_to_brak(12, "h") == approx(0)
    assert gcem.eps_to_brak(8.56, "c") == approx(0 + correction, abs=acc)
    assert gcem.eps_to_brak(7.56, "c") == approx(-1 + correction, abs=acc)
    assert gcem.eps_to_brak(9.56, "c") == approx(1 + correction, abs=acc)



def test_cpn():
    assert gcem.cpn(0, 0) == approx(0)
    assert gcem.cpn(1, 1) == approx(1)

    def cpn_david(x, y):
        # -0.0667 is the correction factor for molar masses since
        # the abundances are in terms of number fractions
        return (np.log10(10 ** (x+8.56 - 0.0667) + 10 ** (y+7.98)) 
                - np.log10(10 ** (8.56 - 0.0667) + 10 ** 7.98)
                )

    x = np.random.uniform(-2, 2, 1000)
    y = np.random.uniform(-2, 2, 1000)

    assert gcem.cpn(x, y) == approx(cpn_david(x, y), abs=1e-3)


def test_cmn():
    assert gcem.cmn(0, 0) == approx(0)
    assert gcem.cmn(1, 1) == approx(1)


    def cmn_david(x, y):
        # -0.0667 is the correction factor for molar masses since
        # the abundances are in terms of number fractions
        return (np.log10(10 ** (x+8.56 - 0.0667) - 10 ** (y+7.98)) 
                - np.log10(10 ** (8.56 - 0.0667) - 10 ** 7.98)
                )
    x = np.random.uniform(-2, 2, 1000)
    y = x + np.random.uniform(-2, 0.4, 1000)

    assert gcem.cmn(x, y) == approx(cmn_david(x, y), abs=1e-3)





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

