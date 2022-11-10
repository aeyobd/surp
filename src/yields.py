import vice
import numpy as np
from vice.yields.agb import interpolator
from scipy.integrate import quad

from vice.yields.presets import JW20
# vice.yields.ccsne.settings['o'] = 0.015
# vice.yields.ccsne.settings['fe'] = 0.0012
# vice.yields.ccsne.settings['sr'] = 3.5e-8
# vice.yields.sneia.settings['o'] = 0
# vice.yields.sneia.settings['fe'] = 0.0017
# vice.yields.sneia.settings['sr'] = 0
# "cristallo11" agb yields for O, Fe, and Sr
def n_agb(m, z, slope = 9.0e-4):
    return slope * m * (z / 0.014)

def set_yields():
    vice.yields.ccsne.settings['n'] = 3.6e-4
    vice.yields.agb.settings['n'] = n_agb

    # we are changing the default c yield from 0.002, all models will change
    vice.yields.ccsne.settings["c"] = 0.005
    vice.yields.sneia.settings["c"] = 0
    vice.yields.agb.settings["c"] = "cristallo11"

    vice.yields.ccsne.settings['o'] = 0.015
    vice.yields.ccsne.settings['fe'] = 0.0012
    vice.yields.ccsne.settings['sr'] = 3.5e-8
    vice.yields.sneia.settings['o'] = 0
    vice.yields.sneia.settings['fe'] = 0.0017
    vice.yields.sneia.settings['fe'] *= 10**0.1 # correction for mdf, used in
    # J22
    vice.yields.sneia.settings['sr'] = 0

set_yields()


class amplified_yields(interpolator):
    def __init__(self, element, study="cristallo11", prefactor=1):
        super().__init__(element, study=study)
        self.prefactor = prefactor

    def __call__(self, mass, Z):
        return super().__call__(mass, Z) * self.prefactor
