import pytest
from pytest import approx
import surp
import vice
import numpy as np
from scipy.integrate import quad


import surp.simulation.sfh_models as sfh_models
import surp.simulation.star_formation_history as sfh_utils


import sys
sys.path.append(".")
import test_create_model

PARAMS = test_create_model.PARAMS
PARAMS2 = test_create_model.PARAMS2

# normalization is tested in test_properties

def test_create_sfh_model():
    param_kwargs = PARAMS.to_dict()
    param_kwargs["sfh_model"] = "static"
    param_kwargs["sfh_kwargs"] = dict()

    params = surp.MWParams(**param_kwargs)
    sfh = sfh_utils.star_formation_history(params)
    
    ts = np.linspace(0, 13.2, 100)
    R = 5
    assert [sfh(R, t) for t in ts] == approx([sfh(R, 0)] * len(ts))

    param_kwargs["sfh_model"] = "insideout"
    param_kwargs["sfh_kwargs"] = dict(
            tau_sfh = 6,
            tau_rise = 2.2
            )

    params = surp.MWParams(**param_kwargs)
    sfh = sfh_utils.star_formation_history(params)
    sfh_model = surp.simulation.sfh_models.insideout(tau_sfh=6, tau_rise=2.2)

    for i in range(len(sfh)):
        r = sfh._radii[i]

        sfh_obs = [sfh(r, t) for t in ts]
        sfh_exp = [sfh_model(t) for t in ts]
        sfh_exp = [s * sfh_obs[-1] / sfh_exp[-1] for s in sfh_exp]

        assert sfh_obs == approx(sfh_exp)


def test_sfh_interpolation():
    # slight offsets from radii should be similar


    # in between values...


    # outside of range???
    pass


def test_sanchez_param():
    param_kwargs = PARAMS.to_dict()
    param_kwargs["sfh_model"] = "insideout"
    param_kwargs["sfh_kwargs"] = dict(
            tau_sfh="0.31sanchez",
            tau_rise = 2.2
            )
    param_kwargs["Re"] = 4
    sfh = sfh_utils.star_formation_history(surp.MWParams(**param_kwargs))

    for i in range(len(sfh)):
        evol = sfh._evol[i]
        R = sfh._radii[i]
        assert evol.tau_sfh == approx(0.31 * sfh_utils.get_sfh_timescale(R, 4))
        assert evol.tau_rise == 2.2

    param_kwargs["sfh_model"] = "twoexp"
    param_kwargs["sfh_kwargs"] = dict(
            t2=3,
            tau1="sanchez",
            tau2=6,
            A2 = 0.5
            )
    param_kwargs["Re"] = 6

    sfh = sfh_utils.star_formation_history(surp.MWParams(**param_kwargs))

    for i in range(len(sfh)):
        evol = sfh._evol[i]
        R = sfh._radii[i]
        assert evol.tau1 == approx(sfh_utils.get_sfh_timescale(R, 6))
        assert evol.tau2 == 6
        assert evol.t2 == 3
        assert evol.A2 == 0.5


def test_r_max_sfh():
    for params in [PARAMS, PARAMS2]:
        sfh = sfh_utils.star_formation_history(params)
        for dR in [0.01, 1, 5]:
            R = PARAMS.max_sf_radius + dR
            t = [0, 1, 2, 3, 4, 5]
            assert [sfh(R, t) for t in t] == approx([0] * len(t))


def test_get_sfh_timescale():
    assert sfh_utils.get_sfh_timescale(8) == approx(15, rel=0.1)
    # test scaling
    assert sfh_utils.get_sfh_timescale(1.6, 1) == approx(15, rel=0.1)
    assert sfh_utils.get_sfh_timescale(0, 5) == approx(5.8, rel=0.1)
    assert sfh_utils.get_sfh_timescale(15) == approx(35, rel=0.1)


def test_twoinfall_sfh():
    param_kwargs = PARAMS.to_dict()
    param_kwargs["sfh_model"] = "twoinfall"
    param_kwargs["sfh_kwargs"] = dict(
            tau1=0.5,
            tau2 = 6.3,
            t2 = 3.8,
            A2 = 0.4
            )
    param_kwargs["r_sun"] = 7.1
    
    sfh = sfh_utils.star_formation_history(surp.MWParams(**param_kwargs))
    sfh_thick = surp.simulation.sfh_models.exp_sfh(0.5)
    sfh_thin = surp.simulation.sfh_models.twoexp(t1=3.8, tau1=6.3, A2=0.0)
    times = np.linspace(0.001, 13.2, 100) #t=0 is funky because of >

    sfh_thick_norm = quad(sfh_thick, 0, 13.2)[0]
    sfh_thin_norm = quad(sfh_thin, 0, 13.2)[0]

    for i in range(len(sfh)):
        evol = sfh._evol[i]
        R = sfh._radii[i]
        assert evol.tau1 == 0.5
        assert evol.tau2 == 6.3
        assert evol.t2 == 3.8

        # A2 depends on thin/thick ratio at specific point
        sigma_thin = np.exp(-(R-7.1) / PARAMS.thin_disk_scale_radius) * PARAMS.thin_to_thick_ratio
        sigma_thick = np.exp(-(R-7.1) / PARAMS.thick_disk_scale_radius)

        A2 = 0.4 * sigma_thin/sigma_thick
        assert evol.A2 == approx(A2)

        sfh_obs = [evol(t) for t in times]
        sfh_exp = [A2 * sfh_thin(t)/sfh_thin_norm + sfh_thick(t)/sfh_thick_norm for t in times]
        sfh_exp = [s * sfh_obs[-1] / sfh_exp[-1] for s in sfh_exp]

        assert sfh_obs == approx(sfh_exp)


def test_BG16_stellar_density():
    param_kwargs = PARAMS.to_dict()

    # single exp if no thin disk...
    param_kwargs["thin_to_thick_ratio"] = 0
    param_kwargs["thick_disk_scale_radius"] = 6.7
    
    params = surp.MWParams(**param_kwargs)
    R = np.linspace(0, 20, 100)
    rho = sfh_utils.BG16_stellar_density(R, params)
    rho_exp = np.exp(-R / 6.7)
    assert rho == approx(rho_exp)

    param_kwargs["thin_to_thick_ratio"] = 3.3
    param_kwargs["thick_disk_scale_radius"] = 5.9
    param_kwargs["thin_disk_scale_radius"] = 2.6
    
    params = surp.MWParams(**param_kwargs)
    R = np.linspace(0, 20, 100)
    rho = sfh_utils.BG16_stellar_density(R, params)
    rho_exp = np.exp(-R / 5.9) + 3.3 * np.exp(-R / 2.6)
    assert rho == approx(rho_exp)


def test_normalized_gradient():
    def test_gradient_plaw(R, params):
        return 1/R

    def test_gradient_exp(R, params):
        return np.exp(-R / 3)


    for test_gradient in [test_gradient_plaw, test_gradient_exp, sfh_utils.BG16_stellar_density]:
        for params in [PARAMS, PARAMS2]:
            grad = sfh_utils.normalized_gradient(params, test_gradient)
            Mtot = params.M_star_MW
            bins = np.array(params.radial_bins)
            areas = np.pi * (bins[1:]**2 - bins[:-1]**2)
            Mtot_act = np.sum(areas * grad)

            # mass works
            assert Mtot_act == approx(Mtot)

            R = sfh_utils.midpoints(bins)
            grad_exp = test_gradient(R, params)
            grad_exp[R > params.max_sf_radius] = 0
            norm = grad[0] / grad_exp[0]

            # gradient is rescaled from test
            assert grad == approx(norm * grad_exp)



def test_midpoints():
    a = [1, 2, 4, 4.5, 4.4]
    assert sfh_utils.midpoints(a) == approx([1.5, 3, 4.25, 4.45])


def test_delta():
    a = [1, 2, 4, 4.5, 4.4]
    assert sfh_utils.delta(a) == approx([1, 2, 0.5, -0.1])

