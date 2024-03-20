# cython: language_level=3

from inspect import Signature, Parameter

import vice # for MLR
from scipy.integrate import quad

from surp._globals import Z_SUN


from libc cimport math as m

cdef double Z_to_MH(double Z):
    return (-8 if Z < 1e-8*Z_SUN else m.log10(Z / Z_SUN))

def get_agb_signature():
    return Signature([
        Parameter("M", Parameter.POSITIONAL_OR_KEYWORD),
        Parameter("Z", Parameter.POSITIONAL_OR_KEYWORD),
        ]
                     )

def get_cc_signature():
    return Signature([ Parameter("Z", Parameter.POSITIONAL_OR_KEYWORD), ])


cdef class ZeroAGB:
    """
    ZeroAGB()

    A convenience class which represents a value of zero AGB yield
    """
    cdef public object __signature__

    def __cinit__(self):
        self.__signature__ = get_agb_signature()
        pass

    def __call__(self, *args, **kwargs):
        return 0

    def __str__(self):
        return "0"

    def __repr__(self):
        return "0"

    
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



cdef class LinAGB:
    """
    LinAGB(eta, y0=0)

    A linear AGB model, used e.g. for nitrogen
    y(m, z) = m (eta z / zsun + y0)
    """

    cdef public double eta
    cdef public double y0
    cdef public object __signature__
    def __init__(self, eta, y0=0):
        self.eta = eta
        self.y0 = y0
        self.__signature__ = get_agb_signature()

    def __call__(self, M, Z):
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

    def __mul__(self, scale):
        other = self.copy()
        other.__imul__(scale)
        return other 

    def __rmul__(self, scale):
        return self.__mul__(scale)

    def copy(self):
        return LinAGB(self.eta, self.y0)


cdef class C_AGB_Model:
    """
    C_AGB_Model(y0, zeta_agb, tau_agb, t_D)

    An analytic version of AGB yields.

    Parameters
    ----------
    y0: the yield at solar metallicity
    zeta: the metallicity dependence
    tau_agb: the agb dtd
    t_D: the minimum delay time
    """

    cdef public double tau_agb, t_D, y0, zeta
    cdef object imf, mlr
    cdef public double A_agb
    cdef public object __signature__

    def __cinit__(self, double y0 = 0.0004, double zeta_agb=-0.02, 
            double tau_agb=0.3, double t_D = 0.15, mlr=vice.mlr.larson1974, imf=vice.imf.kroupa):

        self.tau_agb = tau_agb
        self.t_D = t_D
        self.y0 = y0
        self.zeta = zeta_agb

        self.mlr = mlr
        self.imf = imf
        self.__signature__ = get_agb_signature()

        cdef double m_low = 0.08
        cdef double m_hm = 8
        cdef double m_high = 100

        A_imf = quad(lambda m: m*self.imf(m), m_low, m_high)[0]

        self.A_agb = A_imf / quad(lambda m: m * self.imf(m) * self.y_unnorm(m), 
                m_low, m_hm)[0]

    cdef R(self, t):
        """
        The delay time distribution of C enrichment
        """
        cdef double dt = t - self.t_D
        cdef double R0 = dt/self.tau_agb**2 * m.exp(-dt/self.tau_agb)

        return 0 if dt < 0 else R0


    cdef y_unnorm(self, m):
        return 1/m * m**-4.5 * 1/self.imf(m) * self.R(self.mlr(m))


    cdef double ccall(self, double m, double Z):
        y = self.y0 + self.zeta*(Z-Z_SUN)
        return self.A_agb * y * self.y_unnorm(m) 


    def __call__(self, m, Z):
        """
        self(mass, metallicity)
        """
        return self.ccall(m, Z)


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


cdef class Lin_CC:
    """
    Lin_CC(y0, zeta)

    Constructs a bi-linear piecewise yield model for CCSNe

    Parameters
    ----------
    y0: the yield at solar
    zeta: the slope of the yield at solar

    Methods
    -------
    __call__(Z)
    copy()
    """

    cdef public double y0
    cdef public double zeta
    cdef public object __signature__

    def __cinit__(self, double y0=0.004, double zeta=0.1):
        self.y0 = y0
        self.zeta = zeta

        self.__signature__ = get_cc_signature()

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

    def __call__(self, Z):
        return (self.y0 + self.zeta * (Z - Z_SUN))

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} (Z - Z0)"

    def copy(self):
        return Lin_CC(y0=self.y0, zeta=self.zeta)



cdef class BiLin_CC:
    """
    C_CC_Model(y0, zeta, Z1, y1, zeta1)

    Constructs a bi-log-linear piecewise yield model for CCSNe

    Parameters
    ----------
    y0: the yield at solar
    zeta: the slope of the yield at solar
    Z1: the metallicity below which lerp to y1
    y1: the yield at Z=0

    Methods
    -------
    __call__(Z)
    copy()
    """

    cdef public double y0
    cdef public double zeta
    cdef public double y1
    cdef public double Z1
    cdef public double zeta1
    cdef public object __signature__

    def __cinit__(self, double y0=0.004, double zeta=0.1, 
                  double Z1=0.008, double y1=8.67e-4):
        self.y0 = y0
        self.zeta = zeta

        self.y1 = y1
        self.Z1 = Z1
        self.__signature__ = get_cc_signature()

        y_2 = zeta * (Z1 - Z_SUN) + y0
        self.zeta1 = (y_2-y1)/(Z1)


    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        self.y1 *= scale
        self.zeta1 *= scale
        return self

    def __mul__(self, scale):
        other = self.copy()
        other.__imul__(scale)
        return other

    def __rmul__(self, scale):
        return self.__mul__(scale)



    def __call__(self, Z):
        return (self.y0 + self.zeta * (Z - Z_SUN)
                if Z >= self.Z1 
                else self.y1 + self.zeta1 * Z
                )

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} log(Z/Z0), Z>={self.Z1:0.2e}; {self.y1:0.2e} + {self.zeta1:0.2e} Z, else"

    def copy(self):
        return BiLin_CC(y0=self.y0, zeta=self.zeta, yl = self.yl, Z1=self.Z1)



cdef class LogLin_CC:
    """
    C_CC_Model(y0, zeta)


    Constructs a log-linear ccsne model
    y = y_0 + b*log(Z / Z_sun)
    where b = zeta * Z_sun / log(10) so zeta is consistent

    Parameters
    ----------
    y0: the yield at solar
    zeta: the slope of the yield at solar

    Methods
    -------
    __call__(Z)
    copy()
    """

    cdef public double y0
    cdef public double zeta
    cdef double slope
    cdef public object __signature__

    def __cinit__(self, double y0=0.004, double zeta=0.1):
        self.y0 = y0
        self.zeta = zeta
        self.slope = zeta * Z_SUN * m.log(10)
        self.__signature__ = get_cc_signature()

    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        self.slope *= scale
        return self

    def __mul__(self, scale):
        other = self.copy()
        other.__imul__(scale)
        return other

    def __rmul__(self, scale):
        return self.__mul__(scale)

    def __call__(self, Z):
        return (self.y0 + self.slope * Z_to_MH(Z))

    def __str__(self):
        return f"{self.y0:0.2e} + {self.slope:0.2e} log(Z/Z0)"

    def copy(self):
        return LogLin_CC(y0=self.y0, zeta=self.zeta)



cdef class BiLogLin_CC:
    """
    BiLogLin_CC(y0, zeta, Z1, y1)

    Constructs a bi-linear piecewise yield model for CCSNe

    Parameters
    ----------
    y0: the yield at solar
    zeta_0: the slope of the yield at solar
    Z1: the metallicity below which lerp to y1
    y1: the yield at Z=0

    Methods
    -------
    __call__(Z)
    copy()
    """

    cdef public double y0
    cdef public double zeta
    cdef public double y1
    cdef double slope
    cdef double slope1
    cdef public object __signature__


    def __cinit__(self, double y0=0.004, double zeta=0.1, 
                  double y1=8.67e-4):
        cdef double slope = Z_SUN * zeta * m.log(10)
        self.y0 = y0
        self.zeta = zeta

        self.y1 = y1
        self.__signature__ = get_cc_signature()
        self.slope = zeta * Z_SUN * m.log(10)


    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        self.y1 *= scale
        self.slope *= scale
        self.slope1 *= scale
        return self


    def __mul__(self, scale):
        other = self.copy()
        other.__imul__(scale)
        return other

    def __rmul__(self, scale):
        return self.__mul__(scale)



    def __call__(self, Z):
        return max(self.y1, self.y0 + self.slope*Z_to_MH(Z))

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} log(Z/Z0), Z>={self.Z1:0.2e}; {self.y1:0.2e} + {self.zeta1:0.2e} Z, else"

    def copy(self):
        return BiLin_CC(y0=self.y0, zeta=self.zeta, yl = self.yl, Z1=self.Z1)

