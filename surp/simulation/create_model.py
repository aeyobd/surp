import numpy as np
import vice

from .star_formation_history import star_formation_history 
from .._globals import Z_SUN
from . import properties


def create_model(params):
    """"
    This function wraps various settings to make running VICE multizone models
    easier for the carbon paper investigation. 
    See Parameters for documentation on the options used to create the model.

    This function directly uses the following params:
    - params.zone_width
    - params.filename
    - params.n_stars
    - params.simple
    - params.verbose
    - params.N_star_tot
    - params.migration_mode
    - params.mode
    - params.timestep
    - params.t_d_ia
    - params.RIa
    - params.smoothing
    - params.tau_ia
    - params.m_upper
    - params.m_lower
    - params.Z_solar

    Other parameters are passed to subfunctions create_migration, mass_loading,
    star_formation_history, get_imf, and set_sf_law.
    """


    model = vice.milkyway(
        zone_width = params.zone_width,
        name = params.filename,
    )

    model.dt = params.timestep
    model.n_stars = params.n_stars
    model.verbose = params.verbose
    model.simple = params.simple

    model.smoothing = params.smoothing
    model.IMF = properties.get_imf(params)
    model.RIa = params.RIa
    model.tau_ia = params.tau_ia
    model.delay = params.t_d_ia
    model.m_upper = params.m_upper
    model.m_lower = params.m_lower

    model.migration_mode = params.migration_mode

    model.mode = params.mode
    model.N = params.N_star_tot

    model.Z_solar = Z_SUN
    model.bins = np.arange(-3, 3, 0.01) # don't use this so is okay
    model.elements = ("fe", "o", "mg", "n", "c")

    model.evolution = star_formation_history(params)
    model.mass_loading = properties.mass_loading(params)
    model.migration.stars = properties.create_migration(model.annuli, params)
    # no gas migration

    print(model.migration.stars)

    properties.set_sf_law(model, params)

    return model


