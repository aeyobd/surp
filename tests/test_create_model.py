import surp
import vice
import os
from pytest import approx

def get_test_params():
    params = surp.simulation.MWParams(
        filename = "test",
        zone_width = 10,
        n_stars = 2,
        simple = False,
        verbose = True,

        mode = "sfr",
        imf = "kroupa",
        timestep=5,
        t_d_ia = 0.15,
        RIa = "plaw",
        smoothing = 0.00,
        tau_ia = 1.5,
        m_lower = 0.08,
        m_upper = 100,

        migration = "gaussian",
        migration_mode = "sqrt",
        save_migration=False,
        migration_kwargs = dict(
            sigma_r8 = 1.2,
            tau_power = 0.4,
            R_power = 0.2,
            hz_s = 0.05,
            tau_s_z = 2.2,
            R_s = 5.1,
            ),

        sf_law = "J21",
        sf_law_kwargs = dict(
            present_day_molecular = 2.1,
            ),
        Re = 5.5,

        sfh_model = "insideout",
        sfh_kwargs = dict(
            tau_sfh = "sanchez",
            tau_rise=2,
            ),

        max_sf_radius = 17,
        M_star_MW = 4e10,
        thick_disk_scale_radius = 2.3,
        thin_disk_scale_radius = 2.1,
        thin_to_thick_ratio = 5.2,
        r_sun = 8.1,

        MH_grad_R0 = 5,
        MH_grad_MH0 = -0.1,
        MH_grad_in = -0.05,
        MH_grad_out = -0.1,
        eta_scale = 0.8,
        r = 0.412,
        tau_star_sfh_grad = 0,
            )

    return params

def get_test_params2():
    DIR = os.path.dirname(os.path.abspath(__file__))
    fname = f"{DIR}/params_test.toml"
    params = surp.simulation.MWParams.from_file(fname)
    return params


PARAMS = get_test_params()
PARAMS2 = get_test_params2()


surp.set_yields()
MODEL = None
MODEL2 = None



def test_create_model():
    global MODEL, MODEL2
    MODEL = surp.simulation.create_model(PARAMS)
    MODEL2 = surp.simulation.create_model(PARAMS2)

    assert isinstance(MODEL, vice.milkyway)
    assert isinstance(MODEL2, vice.milkyway)



def check_model_params(model, params):
    assert model.name == params.filename
    assert model.verbose == params.verbose
    assert model.simple == params.simple
    assert model.elements == ("fe", "o", "mg", "n", "c")
    assert model.IMF == params.imf
    assert isinstance(model.mass_loading, surp.simulation.properties.mass_loading)
    assert model.dt == params.timestep
    assert model.delay == params.t_d_ia
    assert model.RIa == params.RIa
    assert model.smoothing == params.smoothing
    assert model.tau_ia == params.tau_ia
    assert model.m_upper == params.m_upper
    assert model.m_lower == params.m_lower
    assert model.Z_solar == 0.016

    assert model.annuli[0] == 0
    assert model.annuli[-1] >= 20
    dr_model = [model.annuli[i+1] - model.annuli[i] for i in range(len(model.annuli)-1)]
    dr_expected = [params.zone_width]*(len(model.annuli) - 1)
    assert dr_model == approx(dr_expected)


def test_check_model_params():
    check_model_params(MODEL, PARAMS)
    check_model_params(MODEL2, PARAMS2)

def test_params_are_different():
    for key in PARAMS.to_dict():
        if key in ("migration_mode",):
            continue
        assert getattr(PARAMS, key) != getattr(PARAMS2, key)


def test_sfh():
    # most of these are much better tested with a complete model
    # for example, the normalization.
    # here, we just check some functional evolution
    sfh = MODEL.evolution
    assert isinstance(sfh, surp.simulation.star_formation_history.star_formation_history)

def test_run():
    MODEL.run(PARAMS.times, overwrite=True, pickle=True)
    assert os.path.exists("test.vice")

    MODEL2.run(PARAMS2.times, overwrite=True, pickle=True)
    assert os.path.exists("test2.vice")

    # close migration to flush the data to disk for later
    MODEL2.migration.stars.close_file()
