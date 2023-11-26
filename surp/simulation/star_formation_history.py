from . import models
from .._globals import  MAX_SF_RADIUS, MAX_RADIUS
from .models.model_utils import get_bin_number, interpolate, gradient
import numpy as np
import vice



def create_sf_law(model, conroy_sf=False, spec="insideout"):
    for zone in model.zones:
       zone.Mg0 = 0.

    for i in range(model.n_zones):
        R1 = model.annuli[i]
        R2 = model.annuli[i+1]
        R = (R1 + R2)/2

        if R <= MAX_SF_RADIUS:
            area = np.pi * (R2**2 - R1**2)
            if conroy_sf:
                model.zones[i].tau_star = conroy_sf_law(area)
            elif spec=="twoinfall":
                model.zones[i].tau_star = twoinfall_sf_law(area)
            else:
                model.zones[i].tau_star = vice.toolkit.J21_sf_law(area, mode="sfr")

def conroy_tau_star(t):
    if t < 2.5:
        tau_st = 50
    elif 2.5 <= t < 3.7:
        tau_st = 50/(1+3*(t-2.5))**2
    else:
        tau_st = 2.36
    return tau_st


def conroy_sf_law(area=None):
    def inner(t, m):
        tau_st = conroy_tau_star(t)
        return vice.toolkit.J21_sf_law(area, tau_st)(t, m)
    return inner


def twoinfall_sf_law(area=None):
    def inner(t, m):
        tau_st = twoinfall_tau_star(t)
        return vice.toolkit.J21_sf_law(area, tau_st)(t, m)
    return inner
    

def twoinfall_tau_star(t):
    if t < 4.1:
        return 1
    else:
        return 2

def create_evolution(spec, burst_size, zone_width):
    """From the parameters, creates a star formation law and 
    returns a function of radius and time of the evolution. 
    """
    kwargs = {}
    kwargs["spec"] = spec
    kwargs["zone_width"] = zone_width

    
    if spec == "lateburst":
        sf_model = models.lateburst
        kwargs["burst_size"] = 1.5 * burst_size
    elif spec == "twoexp":
        sf_model = models.twoexp
        kwargs["tau2"] = 2
        kwargs["A21"] = burst_size
    elif spec == "twoinfall":
        sf_model = models.twoinfall
        kwargs["tau1"] = 2
        kwargs["A21"] = 3.5*burst_size
    elif spec == "threeexp":
        sf_model = models.twoinfall
        kwargs["timescale2"] = 1
        kwargs["amplitude"] = 0.5*burst_size
        kwargs["t1"] = 5
        kwargs["amplitude3"] = 0.2
        kwargs["t2"] = 12
    elif  spec=="insideout":
        sf_model = models.insideout
    else:
        raise ValueError("name not none: ", spec)


    evolution = star_formation_history(sf_model, **kwargs)
    return evolution

class star_formation_history:
    r"""
    The star formation history (SFH) of the model galaxy. This object will be
    used as the ``evolution`` attribute of the ``diskmodel``.

    Parameters
    ----------
    spec : ``str`` [default : "static"]
        A keyword denoting the time-dependence of the SFH.
    **kwargs:
        passed to model

    Calling
    -------
    - Parameters

        radius : ``float``
            Galactocentric radius in kpc.
        time : ``float``
            Simulation time in Gyr.
    """

    def __init__(self, sf_model, zone_width=0.01, **kwargs):
        self._radii = np.arange(zone_width/2, MAX_RADIUS, zone_width)
        self._evol = [sf_model(r) for r in self._radii]
        self.sf_model = sf_model

    def __call__(self, radius, time):
        # The milkyway object will always call this with a radius in the
        # self._radii array, but this ensures a continuous function of radius
        if radius > MAX_SF_RADIUS:
            return 0
        else:
            idx = get_bin_number(self._radii, radius)
            if idx != -1:
                return gradient(radius) * interpolate(self._radii[idx],
                    self._evol[idx](time), self._radii[idx + 1],
                    self._evol[idx + 1](time), radius)
            else:
                return gradient(radius) * interpolate(self._radii[-2],
                    self._evol[-2](time), self._radii[-1], self._evol[-1](time),
                    radius)
    

    def __str__(self):
        return f"{self.sf_model}"

    def __repr__(self):
        return str(self)


