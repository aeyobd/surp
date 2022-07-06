import vice
import numpy as np
from vice.yields.agb import interpolator

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

    vice.yields.ccsne.settings["c"] = 0.002
    vice.yields.sneia.settings["c"] = 0
    vice.yields.agb.settings["c"] = "cristallo11"

    vice.yields.ccsne.settings['o'] = 0.015
    vice.yields.ccsne.settings['fe'] = 0.0012
    vice.yields.ccsne.settings['sr'] = 3.5e-8
    vice.yields.sneia.settings['o'] = 0
    vice.yields.sneia.settings['fe'] = 0.0017
    vice.yields.sneia.settings['sr'] = 0

set_yields()
# for elem in ['c', 'o', 'fe', 'n']: vice.yields.agb.settings[elem] = "karakas16"
# vice.yields.agb.settings["c"] = "cristallo11"
# vice.yields.sneia.settings['fe'] *= 10**0.1


# def y_c_agb(m_c=0.004, m_0=2, b=-0.015, alpha=60, b1=-0.001, b0=-0.002, k=2):
    # def model(mass, Z):
        # return m_c * (1 - alpha*Z) * np.exp(-k*(mass - m_0 - alpha*Z)**2) + b*Z  + b0
# 
    # return model
# 
# def y_c_agb(m_c=0.003, m_0=2.9, b=-0.03, alpha=0.3, k=1.7, gamma=2, b0=-0.002, b1=-0.001):
    # def model(mass, Z):
        # m_shift = gamma/k - m_0 - alpha*np.log10(Z)
        # return m_c * (1 - alpha*np.log10(Z)) * (np.exp(1) * k/gamma)**gamma * (mass + m_shift)**gamma * np.exp(-k*(mass + m_shift)) + b*Z + b1*np.log10(Z) + b0
# 
    # return model

def y_c_agb(m_c=0.008, m0=2.6, alpha=40, k=1.5, gamma=2):
    def model(mass, Z):
        m_shift = gamma/k - m0
        return (mass > -m_shift) * m_c * (1 - alpha*Z) * (np.exp(1) * k/gamma)**gamma * (mass + m_shift)**gamma * np.exp(-k*(mass + m_shift))

    return model

def y_c_agb2(m_c=0.007, m0=1, alpha=40, k=0.7, y0=0):
    def model(mass, Z):
        m = (mass - m0)/k
        return m_c/k * (1 - alpha*Z) * mass**2.3 * np.exp(-m) / (1 + np.exp(-m))**2 + y0
    return model

def y_c_gauss(m_c=0.03, m0=2.6, beta=-30, sigma=0.5):
    def model(mass, Z):
        return m_c*(1 + beta*Z) / np.sqrt(2 * np.pi * sigma) * np.exp(-(mass - m0)**2/(2*sigma**2))

    return model




class amplified_yields(interpolator):
    def __init__(self, element, study="cristallo11", prefactor=1):
        super().__init__(element, study=study)
        self.prefactor = prefactor

    def __call__(self, mass, Z):
        return super().__call__(mass, Z) * self.prefactor
