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


class static(SFHModel):
    r"""
        static()

    The constant SFH model from Johnson et al. (2021). 
    """

    def __init__(self):
        self.norm = 1

    def __call__(self, time=0):
        return self.norm


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

    def __init__(self, tau_rise=2.0, tau_sfh=5):
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

    def __init__(self, tau_sfh, burst_size=1.5, 
                 burst_width=1, burst_time=11.2, tau_rise=2.0):
        self.tau = tau_sfh
        self.tau_rise = tau_rise
        self.burst_time = burst_time
        self.burst_width = burst_width
        self.burst_size = burst_size

        self._insideout = insideout(tau_sfh=tau_sfh, tau_rise=tau_rise)

        self.norm = 1

    def __call__(self, t):
        burst = _gaussian(t, self.burst_time, self.burst_width)

        sfr = self._insideout(t)
        sfr *= (1 + self.burst_size * burst)
        sfr *= self.norm

        return sfr



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
        self.norm = 1


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
        self.tau_sfh = tau_sfh
        self.norm = 1

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

    Parameters
    ----------
    t1 : float [default 4.1]
        The time of the thick disk formation
    t2 : float [default 13.2]
        The present-day time
    tau1 : float [default 2]
        The decay timescale for the thick disk
    tau2 : float [set from insideout.timescale]
        The decay timescale for the thin disk
    A21 : float [default 3.47]
        The ratio between thin and thick disk populations
    """

    def __init__(self, tau1=2, tau2=1, A21=3.47, t1=4.1, t2=13.2):
        self.norm = 1
        self.kwargs = kwargs

        self.A = 1 / (tau1 * (1 - np.exp(-t1/tau1)))
        self.B = A21 / (tau2 * (1 - np.exp(-(t2-t1)/tau2)))

    def __call__(self, time):
        sfr = self.A * np.exp(-time/self.tau1)
        sfr += (time > self.t1) * self.B * np.exp(-(time-self.t1)/self.tau2)


def _gaussian(x, mu, sigma):
    return np.exp(-0.5 * (x - mu)**2 / sigma**2)
