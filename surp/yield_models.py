import textwrap
from typing import Optional

import numpy as np
from scipy.integrate import quad
from scipy.interpolate import interp1d

import vice
from vice.yields.agb import interpolator
from vice.yields import ccsne, sneia, agb

from surp._globals import Z_SUN
from surp import gce_math as gcem
from surp.utils import isreal, validate, arg_isreal



class ZeroAGB:
    """A convenience class which represents a value of zero AGB yield"""
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return 0

    def __str__(self):
        return "0"

    def __repr__(self):
        return "0"

    
    @arg_isreal(1)
    def __imul__(self, scale):
        return self

    def __mul__(self, scale):
        other = self.copy()
        other.__imul__(scale)
        return other 

    def __rmul__(self, scale):
        return self.__mul__(scale)

    def copy(self):
        return ZeroAGB()



class LinAGB:
    """
    A linear AGB model, used e.g. for nitrogen
    y(m, z) = m (eta z / zsun + y0)
    """
    def __init__(self, eta, y0=0):
        self.eta = eta
        self.y0 = y0

    def __call__(self, M, Z):
        return M * (self.y0 + Z/Z_SUN * self.eta)

    def __str__(self):
        if self.y0 != 0:
            return f"{self.y0:0.2e} M + {self.eta:0.2e} M Z/Z0"
        else:
            return f"{self.eta:0.2e} M Z/Z0"

    @arg_isreal(1)
    def __imul__(self, scale):
        self.y0 *= scale
        self.eta *= scale
        return self

    def __mul__(self, scale):
        other = self.copy()
        other.__imul__(scale)
        return other 

    def __rmul__(self, scale):
        return self.__mul__(scale)

    def copy(self):
        return LinAGB(self.eta, self.y0)


class C_AGB_Model:
    """
    An analytic version of AGB yields.

    Parameters
    ----------
    y_0: the yield at solar metallicity
    zeta: the metallicity dependence
    tau_agb: the agb dtd
    t_d: the minimum delay time
    """

    def __init__(self, y0 = 0.0004, zeta_agb=-0.02, 
            tau_agb=0.3, t_D = 0.15):

        self.tau_agb = tau_agb
        self.t_D = t_D
        self.y0 = y0
        self.zeta = zeta_agb

        self.mlr = vice.mlr.larson1974
        self.imf = vice.imf.kroupa
        m_low = 0.08
        m_high = 8
        A_imf = quad(lambda m: m*self.imf(m), m_low, 100)[0]

        self.A_agb = A_imf / quad(lambda m: m * self.imf(m) * self.y_unnorm(m), 
                m_low, m_high)[0]

    def R(self, t):
        """
        The delay time distribution of C enrichment
        """
        dt = t - self.t_D
        return np.where(dt < 0, 0,
                dt/self.tau_agb**2 * np.exp(-dt/self.tau_agb))


    def y_unnorm(self, m):
        return 1/m * m**-4.5 * 1/self.imf(m) * self.R(self.mlr(m))


    def __call__(self, m, Z):
        y = self.y0 + self.zeta*(Z-Z_SUN)
        return self.A_agb * y * self.y_unnorm(m) 


    @arg_isreal(1)
    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        return self

    def __mul__(self, scale):
        other = self.copy()
        other.__imul__(scale)
        return other 

    def __rmul__(self, scale):
        return self.__mul__(scale)

    def __str__(self):
        return f"({self.y0:0.2e} + {self.zeta:0.2e}(Z-Zo)), t_D={self.t_D:0.2f}, tau={self.tau_agb:0.2f}"

    def copy(self):
        return C_AGB_Model(y0=self.y0, zeta_agb=self.zeta_agb,
            tau_agb=self.tau_agb, t_D=self.t_D)


class C_CC_Model:
    def __init__(self, y0=0.004, zeta=0.1, zl=0.000, yl=8.67e-4):
        self.y0 = y0
        self.zeta = zeta
        self.yl = yl
        self.zl = zl

        if zl > 0:
            y2 = zeta * (zl - Z_SUN) + y0
            self.zeta_l = (y2-yl)/(zl)
        else:
            self.zeta_l = 0
            self.zl = -1

    @arg_isreal(1)
    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        self.yl *= scale
        self.zeta_l *= scale
        return self

    def __mul__(self, scale):
        other = self.copy()
        other.__imul__(scale)
        return other

    def __rmul__(self, scale):
        return self.__mul__(scale)



    def __call__(self, Z):
        return np.where(Z >= self.zl, 
                self.y0 + self.zeta * (Z - Z_SUN), 
                self.yl + self.zeta_l * Z
                )

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} (Z-Z0), Z>={self.zl:0.2e}; {self.yl:0.2e} + {self.zeta_l:0.2e} Z, else"

    def copy(self):
        return C_CC_Model(y0=self.y0, zeta=self.zeta, yl = self.yl, zl=self.zl)






