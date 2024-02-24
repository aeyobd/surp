import numpy as np

import vice

from .star_formation_history import star_formation_history 
from .properties import mass_loading, create_migration, set_sf_law
from ..yields import set_yields
from .._globals import Z_SUN


def create_model(params):
    """"
    This function wraps various settings to make running VICE multizone models
    easier for the carbon paper investigation
    """

    model = vice.milkyway(zone_width=params.zone_width,
            name = params.filename,
            n_stars=params.n_stars,
            N=params.N_star_tot,
            simple=params.simple,
            migration_mode=params.migration_mode,
            )

    model.elements = ("fe", "o", "mg", "n", "c")
    model.dt = params.timestep
    model.bins = np.arange(-3, 3, 0.01) # don't use this so is okay
    model.RIa = params.RIa
    model.Z_solar = Z_SUN

    model.evolution = star_formation_history(params)
    set_sf_law(model, params)
    model.migration.stars = create_migration(params)
    model.mass_loading = mass_loading(params)

    return model

