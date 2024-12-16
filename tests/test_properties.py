import pytest 
from pytest import approx
import surp
import surp.simulation.properties as sp

import sys
sys.path.append(".")
from test_create_model import PARAMS, PARAMS2

import numpy as np
import vice


MODEL = surp.simulation.create_model(PARAMS)
MODEL2 = surp.simulation.create_model(PARAMS2)

def test_gauss_migration_init():
    migration = MODEL.migration.stars
    assert isinstance(migration, vice.toolkit.analytic_migration.analytic_migration_2d)
    assert migration.migration_mode == PARAMS.migration_mode
    assert migration.radial_bins == approx(MODEL.annuli)
    assert migration.verbose == PARAMS.verbose
    assert migration.n_zones == len(MODEL.zones) 
    assert not migration.write
    assert isinstance(migration.final_positions, vice.toolkit.analytic_migration.migration_models.final_positions_gaussian_py)
    final_positions = migration.final_positions

    assert final_positions.sigma_r8 == PARAMS.migration_kwargs["sigma_r8"]
    assert final_positions.tau_power == PARAMS.migration_kwargs["tau_power"]
    assert final_positions.R_power == PARAMS.migration_kwargs["R_power"]
    assert final_positions.hz_s == PARAMS.migration_kwargs["hz_s"]
    assert final_positions.tau_s_z == PARAMS.migration_kwargs["tau_s_z"]
    assert final_positions.R_s == PARAMS.migration_kwargs["R_s"]

def test_hydrodisk_migration():
    migration = MODEL2.migration.stars
    assert isinstance(migration, vice.toolkit.hydrodisk.hydrodiskstars)



def test_sf_law():
    for i in range(len(MODEL.zones)):
        zone = MODEL.zones[i]
        assert isinstance(zone.tau_star, vice.toolkit.J21_sf_law)
    ts0 = MODEL.zones[0].tau_star

    # mol when 2.0e+07 < Sigma gas, so want 
    # TODO: should work for 13.2.........
    assert ts0(12.2, 1e4) == approx(PARAMS.sf_law_kwargs["present_day_molecular"])

    for zone in MODEL2.zones:
        assert isinstance(zone.tau_star, sp.twoinfall_sf_law)
        params = PARAMS2

        assert zone.tau_star.nu1 == params.sf_law_kwargs["nu1"]
        assert zone.tau_star.nu2 == params.sf_law_kwargs["nu2"]
        assert zone.tau_star.t2 == params.sf_law_kwargs["t2"]

def test_conroy_sf_law():
    params = PARAMS.to_dict()
    params["sf_law"] = "conroy22"
    params["sf_law_kwargs"] = {}

    model = surp.simulation.create_model(surp.MWParams(**params))

    sf_law = model.zones[0].tau_star
    assert isinstance(sf_law, surp.simulation.properties.conroy_sf_law)

    # between t=0 and 2.5, constant
    assert sf_law(0) == approx(50)
    assert sf_law(1) == approx(50)
    assert sf_law(2.5) == approx(50)
    
    # lerp between 2.5 and 3.7 Gyr
    assert sf_law(3.1) == approx(6.37, rel=0.01)

    # constant after
    assert sf_law(3.7) == approx(2.36)
    assert sf_law(10) == approx(2.36)
    assert sf_law(100) == approx(2.36)


def test_twoinfall_sf_law():
    sf_law = MODEL2.zones[1].tau_star
    t2 = PARAMS2.sf_law_kwargs["t2"]
    nu1 = PARAMS2.sf_law_kwargs["nu1"]
    nu2 = PARAMS2.sf_law_kwargs["nu2"]

    assert sf_law(0) == approx(1/nu1)
    assert sf_law(0.9*t2) == approx(1/nu1)
    assert sf_law(1.1*t2) == approx(1/nu2)
    assert sf_law(100) == approx(1/nu2)


def test_gradient():
        for params in [PARAMS, PARAMS2]:
            grad = surp.simulation.properties.MH_grad(params)
            assert grad.R0 == params.MH_grad_R0
            assert grad.MH_0 == params.MH_grad_MH0
            assert grad.zeta_in == params.MH_grad_in
            assert grad.zeta_out == params.MH_grad_out

            # check normalization
            assert grad(grad.R0) == approx(grad.MH_0)
        
            h = 1e-6
            # check continuity
            assert grad(grad.R0 + h) == approx(grad.MH_0 + grad.zeta_out * h)
            assert grad(grad.R0 - h) == approx(grad.MH_0 - grad.zeta_in * h)

            # check derivatives
            Rl = grad.R0 - 2*h
            assert (grad(Rl) - grad(Rl - h)) / h == approx(grad.zeta_in)
            Rl = grad.R0 / 2
            assert (grad(Rl) - grad(Rl - h)) / h == approx(grad.zeta_in)

            Rl = grad.R0 + 2*h
            assert (grad(Rl) - grad(Rl - h)) / h == approx(grad.zeta_out)

            Rl = grad.R0 * 2
            assert (grad(Rl) - grad(Rl - h)) / h == approx(grad.zeta_out)



def test_eta_derivation():
    params = PARAMS
    grad = surp.simulation.properties.MH_grad(params)
    eta = MODEL.mass_loading
    r = PARAMS.r

    Rs = np.linspace(0, 20, 100)
    Z = surp.gce_math.brak_to_abund(grad(Rs), "o")
    etas = eta(Rs)

    yo = vice.yields.ccsne.settings["o"] * params.eta_scale
    Zeq = yo / (1 + etas - r + params.tau_star_sfh_grad * Rs)

    filt = etas > 0

    assert Zeq[filt] == approx(Z[filt])
    assert sum(filt) > 5


def test_total_mass():
    out = vice.output("test.vice")
    
    Nzones = len(out.zones.keys())
    Ms_zones = [out.zones[f"zone{i}"].history["mstar"][-1] for i in range(Nzones)]
    Mtot2 = sum(Ms_zones)
    Mtot = sum(out.stars["mass"]) * (1 - PARAMS.r)

    assert Mtot == approx(PARAMS.M_star_MW, 0.01)
    assert Mtot2 == approx(PARAMS.M_star_MW, 0.05)

def test_stellar_gradient():
    out = vice.output("test.vice")
    grad = surp.simulation.star_formation_history.normalized_gradient(PARAMS)
    Rs = PARAMS.radial_bins
    
    masses = [grad[i] * np.pi * (Rs[i+1]**2 - Rs[i]**2) for i in range(len(Rs) - 1)]

    Nzones = len(out.zones.keys())
    Ms_zones = [out.zones[f"zone{i}"].history["mstar"][-1] for i in range(Nzones)]
    
    masses = [m / sum(masses) for m in masses]
    Ms_zones = [m / sum(Ms_zones) for m in Ms_zones]
    
    assert masses == approx(Ms_zones, 0.05)


def test_zone_sfh():
    out = vice.output("test.vice")

    Nzones = len(out.zones.keys())
    for i in range(Nzones):
        R = (PARAMS.radial_bins[i] + PARAMS.radial_bins[i+1]) / 2
        zone = out.zones[f"zone{i}"]
        sfh = MODEL.evolution
        times = zone.history["time"]

        sfh_exp = [sfh(R, t) for t in times]
        sfh_sim = zone.history["sfr"]
        norm = sfh_sim[-1] / sfh_exp[-1]
        sfh_exp = [s * norm for s in sfh_exp]
        assert sfh_sim == approx(sfh_exp)


def test_sfh_gradient():
    out = vice.output("test.vice")
    grad = surp.simulation.properties.MH_grad(PARAMS)
    Rs = np.linspace(0, 20, 100)
    Z = surp.gce_math.brak_to_abund(grad(Rs), "o")
    eta = MODEL.mass_loading
    etas = eta(Rs)
    r = PARAMS.r

    yo = vice.yields.ccsne.settings["o"] * PARAMS.eta_scale
    Zeq = yo / (1 + etas - r + PARAMS.tau_star_sfh_grad * Rs)

    filt = etas > 0

    assert Zeq[filt] == approx(Z[filt])
    assert sum(filt) > 5



