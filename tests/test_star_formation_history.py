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

# the normalization 
# and resulting density gradient are best
# checked by the final model
# see test_vice_model (TODO)

def test_create_sfh_model():
    param_kwargs = PARAMS.to_dict()
    param_kwargs["sfh_model"] = "static"
    param_kwargs["sfh_kwargs"] = dict()

    params = surp.MWParams(**param_kwargs)
    sfh = sfh_utils.star_formation_history(params)
    
    ts = np.linspace(0, 13.2, 100)
    R = 5
    assert [sfh(R, t) for t in ts] == approx([sfh(R, 0)] * len(ts))
    
    # test calling with weird R values & the interpolation
    # test that sfh is just scaled from an instance of the class
    # test sanchez
    # test twoinfall model scalings...



def test_get_sfh_timescale():
    assert sfh_utils.get_sfh_timescale(8) == approx(15, rel=0.1)
    # test scaling
    assert sfh_utils.get_sfh_timescale(1.6, 1) == approx(15, rel=0.1)
    assert sfh_utils.get_sfh_timescale(0, 5) == approx(5.8, rel=0.1)
    assert sfh_utils.get_sfh_timescale(15) == approx(35, rel=0.1)


def test_BG16_stellar_density():
    pass

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

