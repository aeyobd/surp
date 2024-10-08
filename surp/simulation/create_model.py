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
    """


    model = vice.milkyway(
        zone_width = params.zone_width,
        name = params.filename,
    )

    model.n_stars = params.n_stars
    model.simple = params.simple
    model.verbose = params.verbose
    model.N = params.N_star_tot
    model.migration_mode = params.migration_mode

    model.evolution = star_formation_history(params)
    model.mode = params.mode
    model.elements = ("fe", "o", "mg", "n", "c")
    model.IMF = properties.get_imf(params)
    model.mass_loading = properties.mass_loading(params)
    model.dt = params.timestep
    model.bins = np.arange(-3, 3, 0.01) # don't use this so is okay
    model.delay = params.t_d_ia
    model.RIa = params.RIa
    model.smoothing = params.smoothing
    model.tau_ia = params.tau_ia
    model.m_upper = params.m_upper
    model.m_lower = params.m_lower
    model.Z_solar = Z_SUN

    model.migration.stars = properties.create_migration(model.annuli, params)
    print(model.migration.stars)
    # no gas migration
    
    # SF law (Kennicutt-Schmidt), needs to be for each zone
    properties.set_sf_law(model, params)

    return model


