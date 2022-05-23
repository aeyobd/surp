import vice
import numpy as np
from vice.yields.agb import interpolator

vice.yields.ccsne.settings["c"] = 0.002
vice.yields.sneia.settings["c"] = 0
# vice.yields.agb.settings["c"] = "cristallo11"



def y_c_agb(m_c=0.004, m_0=2, b=-0.015, alpha=60, b1=-0.001, b0=-0.002, k=2):
    def model(mass, Z):
        return m_c * (1 - alpha*Z) * np.exp(-k*(mass - m_0 - alpha*Z)**2) + b*Z  + b0

    return model

def y_c_agb(m_c=0.003, m_0=2.9, b=-0.03, alpha=0.3, k=1.7, gamma=2, b0=-0.002, b1=-0.001):
    def model(mass, Z):
        m_shift = gamma/k - m_0 - alpha*np.log10(Z)
        return m_c * (1 - alpha*np.log10(Z)) * (np.exp(1) * k/gamma)**gamma * (mass + m_shift)**gamma * np.exp(-k*(mass + m_shift)) + b*Z + b1*np.log10(Z) + b0

    return model
# vice.yields.sneia.settings['fe'] *= 10**0.1
def y_c_agb(m_c=0.008, m_0=2.2, alpha=20, k=1.5, gamma=2, b0=-0.001):
    def model(mass, Z):
        m_shift = gamma/k - m_0 - alpha*Z
        return m_c * (1 - alpha*Z) * (np.exp(1) * k/gamma)**gamma * (mass + m_shift)**gamma * np.exp(-k*(mass + m_shift)) + b0

    return model



class amplified_yields(interpolator):
    def __init__(self, study="cristallo11", prefactor=1):
        pass
