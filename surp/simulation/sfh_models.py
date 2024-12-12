import numpy as np


class SFHModel:
    """
    An Abstract SFH Model.

    Properties
    ----------
    norm : float
        The normalization of the SFH model.

    Methods
    -------
    __call__(time)
        Returns the SFH model at a given time.
    """

    def __init__(self):
        self.norm = 1


    def __call__(self, time):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()

    @property
    def norm(self):
        """
        The normalization of the SFH model. Default is 1.
        """
        return self._norm

    @norm.setter
    def norm(self, value):
        assert np.isreal(value), f"norm must be real, got {value}"
        assert value > 0, f"norm must be positive, got {value}"
        self._norm = value




class static(SFHModel):
    r"""
        static()

    The constant SFH model from Johnson et al. (2021). 
    Returns 1. unless norm is set.
    """

    def __init__(self):
        super().__init__()

    def __call__(self, time=0):
        return self.norm
    
    def __str__(self):
        return "sfh ∝ 1"


class insideout(SFHModel):
    r"""
        insideout(tau_sfh=5, tau_rise=2)

    The inside-out SFH model from Johnson et al. (2021).
    SFH = A * exp(-t/tau_sfh) * (1 - exp(-t/tau_rise))

    Parameters
    ----------
    tau_rise : float
        The rise timescale of the SFH model.
    tau_sfh : float
        The decay timescale of the SFH model.
    """

    def __init__(self, *, tau_rise=2.0, tau_sfh=5):
        super().__init__()
        self.tau_sfh = tau_sfh
        self.tau_rise = tau_rise
        self.norm = 1


    def __call__(self, time):
        sfr = (
            (1 - np.exp(-time/self.tau_rise)) 
            * np.exp(-time/self.tau_sfh)
            )

        sfr *= self.norm
        return sfr

    def __str__(self):
        return f"sfh ∝ (1-exp(t/{self.tau_rise}) * exp(-t/{self.tau_sfh})"


class lateburst(SFHModel):
    r"""
        lateburst(tau_sfh=5, tau_rise=2, burst_size=1.5, burst_width=1, burst_time=11.2)

    The late-burst SFH model from Johnson et al. (2021). 
    Adds a gaussian multiplicative burst ontop of the inside-out SFH model.

    SFR = insideout * (1 + A exp(-delta t^2 / 2 width^2)

    Parameters
    ----------
    tau_sfh : float
        The decay timescale of the insideout model.
    tau_rise : float
        The timescale of initial insideout rise.
    burst_size : float
        The amplitude of the burst.
    burst_width : float
        The width of the burst.
    burst_time : float
        The time of the burst.

    """

    def __init__(self, *, tau_sfh, burst_size=1.5, 
                 burst_width=1, burst_time=11.2, tau_rise=2.0):
        super().__init__()
        self.tau = tau_sfh
        self.tau_rise = tau_rise
        self.burst_time = burst_time
        self.burst_width = burst_width
        self.burst_size = burst_size

        self._insideout = insideout(tau_sfh=tau_sfh, tau_rise=tau_rise)

    def __call__(self, t):
        burst = _gaussian(t, self.burst_time, self.burst_width)

        sfr = self._insideout(t)
        sfr *= (1 + self.burst_size * burst)
        sfr *= self.norm

        return sfr

    def __str__(self):
        return f"sfh ∝ insideout + burst(t={self.burst_time},w={self.burst_width},A={self.burst_size})"


class exp_sfh(SFHModel):
    r"""
        exp_sfh(tau_sfh=5)

    A simple exponential SFH model
    SFH = A * exp(-t/tau_sfh)

    Parameters
    ----------
    tau_sfh : float
        The decay timescale of the SFH model.
    """

    def __init__(self, tau_sfh=5):
        self.tau_sfh = tau_sfh
        super().__init__()


    def __call__(self, time):
        sfr = np.exp(-time / self.tau_sfh)
        sfr *= self.norm
        return sfr

    def __str__(self):
        return f"sfh ∝ exp(-t/{self.tau_sfh})"



class linexp(SFHModel):
    r"""
    A linear-exponential model
    SFH = A * (t/tau_sfh) * exp(-t/tau_sfh)

    Parameters
    ----------
    tau_sfh : float
        The decay timescale of the SFH model.
    """

    def __init__(self, tau_sfh=5):
        super().__init__()
        self.tau_sfh = tau_sfh

    def __call__(self, time):
        sfr = (time/self.tau_sfh) * np.exp(-time / self.tau_sfh)
        sfr *= self.norm
        return sfr

    def __str__(self):
        return f"sfh ∝ t exp(-t/{self.tau_sfh})"



class twoexp(SFHModel):
    r"""
    A double exponential star formation history mimicing the two infall
    model. See Spitoni et al. (2019, 2020, 2022) and similar papers for 
    the motivation.
    The SFH is given by:

    ```math
    SFH = A_1 * exp(-t/tau1) + A_2 * A_{21} * exp(-(t-t1)/tau2) \theta(t-t1)
    ```
    where `C1` is 
    ```math
    A_i = 1 / (tau_i * (1 - exp(-t2/tau_i)))
    ```

    which gives the ratio between the total density of the thin and thick disk.

    Parameters
    ----------
    tend : float [default 13.2]
        The present-day time (used for normalization between components)
    t1 : float [default 0]
        The time component 1 stars forming
    t2: float [default 4.1]
        The time component 2 stars forming
    tau1 : float [default 2]
        The decay timescale for component 1
    tau2 : float [set from insideout.timescale]
        The decay timescale for component 2
    A2 : float [default 3.47]
        The scale factor for component 2 (relative to component 1).
    """

    def __init__(self, *, tau1=2, tau2=1, A2=3.47, t1=0, t2=4.1, tend=13.2):
        super().__init__()

        # relative normalization of components
        self.A = 1 / (tau1 * (1 - np.exp(-(tend - t1)/tau1)))
        self.B = A2 / (tau2 * (1 - np.exp(-(tend - t2)/tau2)))

        # keep for sanity
        self.tend = tend
        self.A2 = A2

        self.t1 = t1
        self.t2 = t2
        self.tau1 = tau1
        self.tau2 = tau2

    def __call__(self, time):
        sfr = self.A * np.exp(-(time - self.t1)/self.tau1) * (time > self.t1)
        sfr += self.B * np.exp(-(time - self.t2)/self.tau2) * (time > self.t2)

        return sfr * self.norm

    def __str__(self):
        return f"sfh ∝ truncexp(t,{self.t1},{self.tau1}) + {self.A2} truncexp(t,{self.t2},{self.tau2})"


class threeexp(SFHModel):
    """
    A triple exponential star formation history mimicing the three infall.


    Parameters
    ----------
    tend : float [default 13.2]
        The present-day time (used for normalization between components)
    t1 : float [default 0]
        The time component 1 stars forming
    t2: float [default 4.1]
        The time component 2 stars forming
    t3: float [default 8.2]
        The time component 3 stars forming

    tau1 : float [default 2]
        The decay timescale for component 1
    tau2 : float [set from insideout.timescale]
        The decay timescale for component 2
    tau3 : float [set from insideout.timescale]
        The decay timescale for component 3

    A2 : float [default 3.47]
        The scale factor for component 2 (relative to component 1).
    A3 : float [default 3.47]
        The scale factor for component 3 (relative to component 1).
    """

    def __init__(self, *, 
                 tau1=2, tau2=1, tau3=1, 
                 A2=3.47, A3=3.47, 
                 t1=0, t2=4.1, t3=8.2, 
                 tend=13.2
                ):
        super().__init__()

        # relative normalization of components
        self.A = 1 / (tau1 * (1 - np.exp(-(tend - t1)/tau1)))
        self.B = A2 / (tau2 * (1 - np.exp(-(tend - t2)/tau2)))
        self.C = A3 / (tau3 * (1 - np.exp(-(tend - t3)/tau3)))

        # keep for sanity
        self.tend = tend
        self.A2 = A2
        self.A3 = A3

        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.tau1 = tau1
        self.tau2 = tau2
        self.tau3 = tau3

    def __call__(self, time):
        sfr = self.A * np.exp(-(time - self.t1)/self.tau1) * (time > self.t1)
        sfr += self.B * np.exp(-(time - self.t2)/self.tau2) * (time > self.t2)
        sfr += self.C * np.exp(-(time - self.t3)/self.tau3) * (time > self.t3)
        return sfr * self.norm

    def __str__(self):
        return "sfh ∝ truncexp(t,{self.t1},{self.tau1}) + {self.A2} truncexp(t,{self.t2},{self.tau2}) + {self.A3} truncexp(t,{self.t3},{self.tau3})"



def _gaussian(x, mu, sigma):
    """
    _gaussian(x, mu, sigma)

    unnormalized gaussian function with mean mu and width sigma
    used for lateburst SFH
    """
    return np.exp(-0.5 * (x - mu)**2 / sigma**2)
