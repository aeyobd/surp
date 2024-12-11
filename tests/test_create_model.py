import surp
import vice
import os

def get_test_params():
    params = surp.simulation.MWParams(
        filename = "test",
        zone_width = 3.3,
        n_stars = 2,
        simple = False,
        verbose = True,
        migration_mode = "diffusion",
        migration = "gaussian",
        sigma_R = 0.83,
        save_migration=False,
        mode = "sfr",
        imf = "kroupa",
        timestep=0.2,
        t_d_ia = 0.15,
        RIa = "plaw",
        smoothing = 0.00,
        tau_ia = 1.5,
        m_lower = 0.08,
        m_upper = 100,

        sf_law = "J21",
        tau_star0 = 2.0,
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


def test_run():
    MODEL.run(PARAMS.times, overwrite=True, pickle=True)
    assert os.path.exists("test.vice")


def check_model_params(model, params):
    assert model.name == params.filename
    assert model.verbose == params.verbose
    assert model.simple == params.simple
    assert model.elements == ("fe", "o", "mg", "n", "c")
    assert isinstance(model.mass_loading, surp.simulation.properties.mass_loading)
    assert model.dt == params.timestep
    assert model.delay == params.t_d_ia
    assert model.RIa == params.RIa
    assert model.m_upper == params.m_upper
    assert model.m_lower == params.m_lower
    assert model.Z_solar == 0.016


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
