import numpy as np


class static:
    r"""
    The constant SFH model from Johnson et al. (2021).
    """
    def __init__(self, radius, dt = 0.01, dr = 0.1):
        self.norm = 1

    def __call__(self):
        return self.norm


class insideout:
    r"""
    The inside-out SFH model from Johnson et al. (2021).

    Parameters
    ----------
    radius : float
        The galactocentric radius in kpc of a given annulus in the model.
    dt : float [default : 0.01]
        The timestep size of the model in Gyr.
    dr : float [default : 0.1]
        The width of the annulus in kpc.
    """
    def __init__(self, radius, tau_rise=2.0, tau_sfh=5):
        kwargs = {"norm": 1, "tau": tau_sfh, "tau_rise": tau_rise}
        self.kwargs = kwargs
        self.norm = 1


    def __call__(self, time):
        return self.norm * modified_exponential(time, **self.kwargs)

    def __str__(self):
        return f"sfh ∝ (1-exp(t/{self.tau_rise}) * exp(-t/{self.tau})"


class lateburst:
    r"""
    The late-burst SFH model from Johnson et al. (2021).

    Parameters
    ----------
    radius : float
        The galactocentric radius in kpc of a given annulus in the model.
    dt : float [default : 0.01]
        The timestep size of the model in Gyr.
    dr : float [default : 0.1]
        The width of the annulus in kpc.
    """

    def __init__(self, tau_sfh, burst_size=1.5, 
                 burst_width=1, burst_time=11.2, tau_rise=2.0):
        self.tau = tau_sfh
        self.tau_rise = tau_rise
        self.burst_time = burst_time
        self.burst_width = burst_width
        self.burst_size = burst_size

        self.norm = 1

    def __call__(self, t):
        return self.norm * modified_exponential(t, self.tau, self.tau_rise) * (
                1 + gaussian(t, self.burst_time, self.burst_width, self.burst_size) )


class twoexp:
    r"""
    A double exponential star formation history mimicing the two infall
    model. 

    Parameters
    ----------
    radius : float
        The galactocentric radius in kpc of a given annulus in the model.
    dt : float [default : 0.01]
        The timestep size of the model in Gyr.
    dr : float [default : 0.1]
        The width of the annulus in kpc.

    ** kwargs passeed to ```.utils.double_exponential.__init__```
    -------------------------------------------------------------
    t1 : float [default 4.1]
        The time of the thick disk formation
    t2 : float [default 13.2]
        The present-day time
    tau1 : float [default 2]
    tau2 : float [set from insideout.timescale]
        The decay timescale for the thin disk
    A21 : float [default 3.47]
        The ratio between thin and thick disk populations

    """

    def __init__(self, radius, **kwargs):
        self.norm = 1
        self.kwargs = kwargs

    def __call__(self, time):
        return self.norm * double_exponential(time, **self.kwargs)



class threeexp:
    def __init__(self, radius, **kwargs):
        self.kwargs = kwargs
        self.norm = 1

    def __call__(self, time):
        return self.norm * double_exponential(time, norm=self.norm, **self.kwargs)



def modified_exponential(t, tau, tau_rise, norm=1):
    return (1 - np.exp(-t/tau_rise)) * exponential(t, tau) 


def exponential(t, tau, norm=1):
    return np.exp(-t / tau)


def gaussian(t, mean, std, norm=1):
    return np.exp( -(t-mean)**2 / (2*std**2) )


def double_exponential(t, norm=1, tau1=2, tau2=1, A21=3.47, t1=4.1, t2=13.2):
    A = 1 / (tau1 * (1 - np.exp(-t1/tau1)))
    B = A21 / (tau2 * (1 - np.exp(-(t2-t1)/tau2)))
    B *= (t > self.t1)

    return ( 
       A * np.exp(-t/tau1) + 
       B * np.exp((-t+t1)/tau2) )


def triple_exponential(t, A32=0.4, tau3=0.15, t2=11, t3=13.2, **kwargs):
    C = A32  / (tau3 * (1 - np.exp(-(t3-t2)/tau3)))
    C *= (t > self.t2)

    return  ( double_exponential(t, t2=t2, **kwargs)
        + C * np.exp(-(t-t2)/tau3)
        )


