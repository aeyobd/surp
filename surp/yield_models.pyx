# cython: language_level=3

from inspect import Signature, Parameter

import vice # for MLR
from scipy.integrate import quad

from surp._globals import Z_SUN


from libc cimport math as m

cdef double Z_to_MH(double Z):
    return (-8 if Z < 1e-8*Z_SUN else m.log10(Z / Z_SUN))



cdef class AbstractCC:
    """
    AbstractCC()
    
    An abstract class for core-collapse supernova yield models
    Classes must implement __imul__, copy, and ccall(self, Z), and __init__
    """
    def __call__(self, Z):
        """
        self(mass, metallicity)
        """
        return self.ccall(Z)

    def __mul__(self, scale):
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
    def __mul__(self, scale):
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

    def __cinit__(self, double y0 = 0.0004, double zeta=-0.0002, 
            double tau_agb=0.3, double t_D = 0.15, mlr=vice.mlr.larson1974, imf=vice.imf.kroupa):
        cdef double m_low = 1.2
        cdef double m_hm = 8
        cdef double m_high = 100

        self.tau_agb = tau_agb
        self.t_D = t_D
        self.y0 = y0
        self.zeta = zeta

        self.mlr = mlr
        self.imf = imf


        A_imf = quad(lambda m: m*self.imf(m), m_low, m_high)[0]

        self.A_agb = A_imf / quad(lambda m: m * self.imf(m) * self.y_unnorm(m), 
                m_low, m_hm)[0]


    cdef R(self, double t):
        """
        The delay time distribution of C enrichment
        """
        cdef double dt = t - self.t_D
        cdef double R0 = dt/self.tau_agb**2 * m.exp(-dt/self.tau_agb)

        return 0 if dt < 0 else R0


    cdef y_unnorm(self, double m):
        return 1/m * m**-4.5 * 1/self.imf(m) * self.R(self.mlr(m))


    cdef double ccall(self, double m, double Z):
        cdef double M_H = Z_to_MH(Z)
        y = self.y0 + self.zeta*M_H
        return self.A_agb * y * self.y_unnorm(m) 


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
    Exp_CC(y0, zeta)

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

    def __cinit__(self, double y0=0.004, double zeta=0.1):
        self.y0 = y0
        self.zeta = zeta



    cpdef ccall(self, double Z):
        return (self.y0 + self.zeta * (Z - Z_SUN))

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} (Z - Z0)"

    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        return self

    def copy(self):
        return Lin_CC(y0=self.y0, zeta=self.zeta)


cdef class LogLin_CC(AbstractCC):
    """
    LogLin_CC(y0, A1)


    Constructs a inear ccsne model
    y = y_0 + A1 * [M/H]

    Parameters
    ----------
    y0: the yield at solar
    A2: the slope of the yield at solar

    Methods
    -------
    __call__(Z)
    copy()
    """

    cdef public double y0
    cdef public double B
    cdef double slope

    def __cinit__(self, double y0=0.004, double B=0.1):
        self.y0 = y0
        self.B = B
        # self.slope = zeta * Z_SUN * m.log(10)

    def __imul__(self, scale):
        self.y0 *= scale
        self.B *= scale
        # self.slope *= scale
        return self


    cpdef double ccall(self, double Z):
        cdef double M_H = Z_to_MH(Z)
        return (self.y0 + self.B * M_H)

    def __str__(self):
        return f"{self.y0:0.2e} + {self.B:0.2e} [M/H]"

    def copy(self):
        return LogLin_CC(y0=self.y0, B=self.B)



cdef class BiLogLin_CC(AbstractCC):
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
    cdef public double B
    cdef public double y1

    def __cinit__(self, double y0=0.004, double B=0.1, 
                  double y1=8.67e-4):
        # cdef double slope = Z_SUN * zeta * m.log(10)
        self.y0 = y0
        self.B = B
        self.y1 = y1
        # self.slope = zeta * Z_SUN * m.log(10)


    def __imul__(self, scale):
        self.y0 *= scale
        self.B *= scale
        self.y1 *= scale
        return self

    cpdef double ccall(self, Z):
        cdef double M_H = Z_to_MH(Z)
        return max(self.y1, self.y0 + self.B*M_H)


    def __str__(self):
        return f"{self.y0:0.2e} + {self.B:0.2e} [M/H] or {self.y1:0.2e}, else"

    def copy(self):
        return BiLogLin_CC(y0=self.y0, B=self.B, y1=self.y1)



cdef class BiLin_CC(AbstractCC):
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

    def __cinit__(self, double y0=0.004, double zeta=0.1, 
                  double Z1=0.008, double y1=8.67e-4):
        self.y0 = y0
        self.zeta = zeta

        self.y1 = y1
        self.Z1 = Z1

        y_2 = zeta * (Z1 - Z_SUN) + y0
        self.zeta1 = (y_2-y1)/(Z1)


    def __imul__(self, scale):
        self.y0 *= scale
        self.zeta *= scale
        self.y1 *= scale
        self.zeta1 *= scale
        return self


    cpdef double ccall(self, Z):
        return (self.y0 + self.zeta * (Z - Z_SUN)
                if Z >= self.Z1 
                else self.y1 + self.zeta1 * Z
                )

    def __str__(self):
        return f"{self.y0:0.2e} + {self.zeta:0.2e} log(Z/Z0), Z>={self.Z1:0.2e}; {self.y1:0.2e} + {self.zeta1:0.2e} Z, else"

    def copy(self):
        return BiLin_CC(y0=self.y0, zeta=self.zeta, yl = self.yl, Z1=self.Z1)



cdef class Quadratic_CC(AbstractCC):
    """
    Quadratic(A, B, C)

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
    cdef public double A
    cdef public double B
    cdef double vertex
    cdef double y_v


    def __cinit__(self, double A=1e-3, double B=2e-3, double y0=3e-3):
        self.A = A
        self.B = B
        self.y0 = y0

        self.vertex = -B/(2*A)
        self.y_v = A*self.vertex**2 + B*self.vertex + y0


    def __imul__(self, scale):
        self.A *= scale
        self.B *= scale
        self.y0 *= scale
        return self


    cpdef ccall(self, Z):
        cdef double M_H = Z_to_MH(Z)
        if M_H > self.vertex:
            return self.A*M_H**2 + self.B*M_H + self.y0
        else:
            return self.y_v

    def __str__(self):
        return f"{self.A:0.2e} MH^2 + {self.B:0.2e} MH + {self.y0:0.2e}"

    def copy(self):
        return Quadratic_CC(A=self.A, zeta=self.B, y0=self.y0)

