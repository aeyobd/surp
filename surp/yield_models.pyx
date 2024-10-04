# cython: language_level=3

"""
A few yield models which we find useful.
Some common definitions

y0: the yield at solar metallicity
zeta: the logarithmic yield slope at solar metallicity
    zeta = d y / d log10 Z

"""

from inspect import Signature, Parameter

import vice # for MLR
from scipy.integrate import quad

from surp._globals import Z_SUN


from libc cimport math as m

cdef double Z_to_MH(double Z):
    return (-8 if Z < 1e-8*Z_SUN else m.log10(Z / Z_SUN))



"""
Given zeta (the logarithmic slope d y / d log10 Z), returns
the linear slope $d y / d Z = zeta / (Z_SUN * ln(10))$
"""
def zeta_to_slope(zeta):
    return zeta / (Z_SUN * m.log(10))


cpdef chabrier(double mass):
    """
    Returns the chabrier [1] imf (taken from table 1 for single stars).
    the single argument is the mass in solar masses.

    The Chabrier


    [1] Chabrier, G. 2003, PASP, 115(809), 763-795
    """
    cdef double A1 = 0.158
    cdef double mc = 0.079
    cdef double sigma = 0.69

    cdef double logm = m.log10(mass)

    cdef double xi

    if mass < 0.08:
        xi = 0.
    elif mass < 1:
        xi = A1 * m.exp( -(logm - m.log10(mc))**2 / (2*sigma**2))
    elif logm < 0.54:
        xi = 0.044 * mass**-4.37
    elif logm < 1.26:
        xi = 0.015 * mass**-3.53
    elif logm < 1.8:
        xi = 2.5e-4 * mass**-2.11
    else:
        xi = 0.

    return xi / (m.log(10) * mass)
    


cdef class AbstractCC:
    """
    An abstract class for core-collapse supernova yield models
    Classes must implement __imul__, copy, and ccall(self, Z), and __init__
    """
    def __call__(self, Z):
        """
            self(metallicity)

        returns the net fractional yield for the given metallicity
        """
        return self.ccall(Z)

    def __mul__(self, scale):
        """scales the yield by some factor uniformly"""
        other = self.copy()
        other.__imul__(scale)
        return other 

    def __rmul__(self, scale):
        return self.__mul__(scale)


    def __str__(self):
        return "Abstract CC Model"

    @property
    def __signature__(self):
        return Signature([ Parameter("Z", Parameter.POSITIONAL_OR_KEYWORD), ])


cdef class AbstractAGB:
    """
    Abstract Class for AGB yield model in VICE. Methods must implement
    ccall(m, Z), __imul__, copy, and __init__
    """

    def __mul__(self, scale):
        """scale the yield by some factor uniformly"""
        other = self.copy()
        other.__imul__(scale)
        return other 

    def __rmul__(self, scale):
        return self.__mul__(scale)

    @property
    def __signature__(self):
        return Signature([
            Parameter("M", Parameter.POSITIONAL_OR_KEYWORD),
            Parameter("Z", Parameter.POSITIONAL_OR_KEYWORD),
            ]
                         )


    def __call__(self, m, Z):
        """
            self(mass, metallicity)

        returns the net fractional yield (Y^{AGB}) for the given mass and 
        metallicity
        """
        return self.ccall(m, Z)



cdef class ZeroAGB(AbstractAGB):
    """
    ZeroAGB()

    A convenience class which represents a value of zero AGB yield
    """

    def __cinit__(self):
        pass

    def ccall(self, m, Z):
        return 0

    def __str__(self):
        return "0"

    def __repr__(self):
        return "0"

    def __imul__(self, scale):
        return self

    def copy(self):
        return ZeroAGB()



cdef class LinAGB(AbstractAGB):
    """
    LinAGB(eta, y0=0)

    A linear AGB model, used e.g. for nitrogen
    y(m, z) = m (eta z / zsun + y0)
    """

    cdef public double eta
    cdef public double y0

    def __init__(self, eta, y0=0):
        self.eta = eta
        self.y0 = y0

    cpdef ccall(self, double M, double Z):
        return M * (self.y0 + Z/Z_SUN * self.eta)

    def __str__(self):
        if self.y0 != 0:
            return f"{self.y0:0.2e} M + {self.eta:0.2e} M Z/Z0"
        else:
            return f"{self.eta:0.2e} M Z/Z0"

    def __imul__(self, scale):
        self.y0 *= scale
        self.eta *= scale
        return self

    def copy(self):
        return LinAGB(self.eta, self.y0)



cdef class C_AGB_Model(AbstractAGB):
    r"""
    C_AGB_Model(y0, zeta_agb, tau_agb, t_D)

    An analytic version of AGB yields.

    ```math
    Y_{\rm C}^{\rm AGB} = A \left(y_0 + \zeta [M/H]\right) \frac{\exp(-(t-t_D) / \tau_{\rm AGB}}{t^\gamma} 
    ```

    Parameters
    ----------
    y0: the yield at solar metallicity
    zeta: the metallicity dependence
    tau_agb: the agb dtd
    t_D: the minimum delay time
    gamma: the exponent
    zeta_tau: the metallicity dependence of t_D
    mlr: the mass - lifetime relationship
    imf: the initial mass function
    m_low: the minimum cutoff mass
    """

    cdef public double tau_agb, t_D, y0, zeta
    cdef object imf, mlr
    cdef public double A_agb
    cdef public double m_low, m_hm, m_high
    cdef public double gamma, zeta_tau

    def __cinit__(self, double y0 = 0.0004, double zeta=-0.0002, 
            double tau_agb=0.3, double t_D = 0.15, mlr=vice.mlr.larson1974, 
            double gamma=2, double zeta_tau=0, 
            double m_low = 1.2, 
            imf=vice.imf.kroupa):

        self.m_low = m_low
        imf_low = 0.08
        self.m_hm = 8
        self.m_high = 100

        self.tau_agb = tau_agb
        self.t_D = t_D
        self.y0 = y0
        self.zeta = zeta
        self.gamma = gamma
        self.zeta_tau = zeta_tau

        self.mlr = mlr
        self.imf = imf


        A_imf = quad(lambda m: m*self.imf(m), imf_low, self.m_high)[0]

        self.A_agb = A_imf / quad(lambda m: m * self.imf(m) * self.y_unnorm(m, Z_SUN), 
                imf_low, self.m_high)[0]


    cdef R(self, double t, double Z):
        """
        The delay time distribution of C enrichment
        """
        cdef double dt = t - self.t_D
        cdef double M_H = Z_to_MH(Z)
        cdef double tau = self.tau_agb + self.zeta_tau * M_H
        
        if tau < 0:
            tau = 1e-3
            
        cdef double R0 = 0
        if dt > 0:
            R0 = dt**self.gamma / tau**(self.gamma + 1) * m.exp(-dt/tau)

        return R0


    cdef y_unnorm(self, double m, double Z):
        if m < self.m_low or m > self.m_high:
            return 0
        return 1/m * m**-4.5 * 1/self.imf(m) * self.R(self.mlr(m), Z)


    cpdef double ccall(self, double m, double Z):
        cdef double M_H = Z_to_MH(Z)
        y = self.y0 + self.zeta*M_H
        return self.A_agb * y * self.y_unnorm(m, Z) 


    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        return self


    def __str__(self):
        return f"({self.y0:0.2e} + {self.zeta:0.2e}(Z-Zo)), t_D={self.t_D:0.2f}, tau={self.tau_agb:0.2f}"

    def copy(self):
        return C_AGB_Model(y0=self.y0, zeta=self.zeta, 
               tau_agb=self.tau_agb, t_D=self.t_D, 
               mlr=self.mlr, imf=self.imf)





cdef class Lin_CC(AbstractCC):
    """
    Lin_CC(y0, zeta)

    Constructs a linear piecewise yield model for CCSNe
    y = y_0 + slope * (Z - Z_\\odot)

    Note that the slope is defined as zeta / (Z_\\odot \\ln(10)) as to be 
    the slope in the log10 space where zeta = d y / d Z

    Parameters
    ----------
    y0: the yield at solar
    zeta: the logarithmic yield slope at solar 

    Attributes
    ----------
    slope : the linear slope at solar = zeta / (Z_\\odot \\ln(10))
    """

    cdef public double y0
    cdef public double zeta
    cdef public double slope

    def __cinit__(self, double y0=0.004, double zeta=0.1):
        self.y0 = y0
        self.zeta = zeta
        self.slope = zeta_to_slope(zeta)


    cpdef ccall(self, double Z):
        return (self.y0 + self.slope * (Z - Z_SUN))

    def __str__(self):
        return f"{self.y0:0.2e} + {self.slope:0.2e} (Z - Z0)"

    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        self.slope *= scale
        return self

    def copy(self):
        return Lin_CC(y0=self.y0, zeta=self.zeta, slope=self.slope)



cdef class LogLin_CC(AbstractCC):
    """
    LogLin_CC(y0, A1)


    Constructs a inear ccsne model
    y = y_0 + zeta * [M/H]

    Parameters
    ----------
    y0: the yield at solar
    zeta: the slope of the yield at solar
    """

    cdef public double y0
    cdef public double zeta

    def __cinit__(self, double y0=0.004, double zeta=0.1):
        self.y0 = y0
        self.zeta = zeta

    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        return self


    cpdef double ccall(self, double Z):
        cdef double M_H = Z_to_MH(Z)
        return (self.y0 + self.zeta * M_H)

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} [M/H]"

    def copy(self):
        return LogLin_CC(y0=self.y0, zeta=self.zeta)



cdef class BiLogLin_CC(AbstractCC):
    """
    BiLogLin_CC(y0, zeta, Z1, y1)

    Constructs a bi-linear piecewise yield model for CCSNe
        y = max(y1, y0 + zeta * [M/H])


    Parameters
    ----------
    y0: the yield at solar
    zeta: the slope of the yield at solar
    y1: the yield at Z=0
    """

    cdef public double y0
    cdef public double zeta
    cdef public double y1

    def __cinit__(self, double y0=0.004, double zeta=0.1, 
                  double y1=8.67e-4):
        self.y0 = y0
        self.zeta = zeta
        self.y1 = y1


    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        self.y1 *= scale
        return self

    cpdef double ccall(self, Z):
        cdef double M_H = Z_to_MH(Z)
        return max(self.y1, self.y0 + self.zeta*M_H)


    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} [M/H] or {self.y1:0.2e}, else"

    def copy(self):
        return BiLogLin_CC(y0=self.y0, zeta=self.zeta, y1=self.y1)



cdef class BiLin_CC(AbstractCC):
    """
    C_CC_Model(y0, zeta, Z1, y1, zeta1)

    Constructs a bi-log-linear piecewise yield model for CCSNe


    Parameters
    ----------
    y0: the yield at solar
    zeta: the slope of the yield at solar
    y1: the yield at Z=0
    Z1: the metallicity below which lerp to y1
    """

    cdef public double y0
    cdef public double zeta
    cdef public double slope
    cdef public double y1
    cdef public double Z1
    cdef public double slope1

    def __cinit__(self, double y0=0.004, double zeta=0.1, 
                  double Z1=0.008, double y1=8.67e-4):
        self.y0 = y0
        self.zeta = zeta
        self.slope = zeta_to_slope(zeta)

        self.y1 = y1
        self.Z1 = Z1

        y_2 = self.slope * (Z1 - Z_SUN) + y0
        self.slope1 = (y_2-y1)/(Z1)


    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        self.y1 *= scale
        self.slope1 *= scale
        self.slope *= scale
        return self


    cpdef double ccall(self, Z):
        return (self.y0 + self.slope * (Z - Z_SUN)
                if Z >= self.Z1 
                else self.y1 + self.slope1 * Z
                )

    def __str__(self):
        return f"{self.y0:0.2e} + {self.slope:0.2e} (Z-Z0), Z>={self.Z1:0.2e}; {self.y1:0.2e} + {self.slope1:0.2e} Z, else"

    def copy(self):
        return BiLin_CC(y0=self.y0, zeta=self.zeta, Z1=self.Z1, y1=self.y1)


cdef class Piecewise_CC(AbstractCC):
    """
    Piecewise_CC(y0s, zetas, Zs)

    Constructs a piecewise yield model for CCSNe.
    y = y0s[i] + zetas[i] [M/H] for Z < Zs[i]

    Parameters
    ----------
    y0s: the yields at solar
    zetas: the slopes of the yield at solar
    Zs: list(float)
        The threshold metallicities between pieces. 
        Should be ascending and length of y0s -1 
        
    """

    cdef public list y0s
    cdef public list zetas
    cdef public list Zs

    def __cinit__(self, list y0s, list zetas, list Zs):
        self.y0s = y0s
        self.zetas = zetas
        self.Zs = Zs

    def __imul__(self, scale):
        self.y0s = [y*scale for y in self.y0s]
        self.zetas = [z*scale for z in self.zetas]
        return self

    cpdef double ccall(self, double Z):
        cdef double M_H = Z_to_MH(Z)
        for i, Z_i in enumerate(self.Zs):
            if Z <= Z_i:
                return self.y0s[i] + self.zetas[i] * M_H

        return self.y0s[-1] + self.zetas[-1] * M_H



cdef class Quadratic_CC(AbstractCC):
    """
    Quadratic(A, zeta, y0)

    Constructs a bi-linear piecewise yield model for CCSNe

    y = A [M/H]^2 + zeta [M/H] + y0

    note that we set the yield at the vertex to be constant down to Z=0


    Parameters
    ----------
    y0: the yield at solar
    zeta_0: the slope of the yield at solar
    A: the quadratic coefficient

    Attributes
    ----------
    vertex : the metallicity at which the yield is at extremum
    y_v : the yield at the vertex
    """

    cdef public double y0
    cdef public double A
    cdef public double zeta
    cdef double vertex
    cdef double y_v


    def __cinit__(self, double A=1e-3, double zeta=2e-3, double y0=3e-3):
        self.A = A
        self.zeta = zeta
        self.y0 = y0

        if abs(A) < 1e-10:
            self.vertex = -m.INFINITY
            self.y_v = m.NAN
        else:
            self.vertex = -zeta/(2*A)
            self.y_v = A*self.vertex**2 + zeta*self.vertex + y0


    def __imul__(self, scale):
        self.A *= scale
        self.zeta *= scale
        self.y0 *= scale
        self.y_v *= scale
        return self


    cpdef ccall(self, Z):
        cdef double M_H = Z_to_MH(Z)
        if M_H > self.vertex:
            return self.A*M_H**2 + self.zeta*M_H + self.y0
        else:
            return self.y_v

    def __str__(self):
        return f"{self.A:0.2e} MH^2 + {self.zeta:0.2e} MH + {self.y0:0.2e}"

    def copy(self):
        return Quadratic_CC(A=self.A, zeta=self.zeta, y0=self.y0)



