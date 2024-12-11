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



PARAMS = get_test_params()


surp.set_yields()
MODEL = None



def test_create_model():
    global MODEL
    MODEL = surp.simulation.create_model(PARAMS)
    assert isinstance(MODEL, vice.milkyway)


def test_run():
    MODEL.run(PARAMS.times, overwrite=True, pickle=True)
    assert os.path.exists("test.vice")


