r"""
This file declares the time-dependence of the star formation history at a
given radius in the fiducial inside-out model from Johnson et al. (2021).
"""

from .utils import modified_exponential, get_bin_number, interpolate, double_exponential
from .normalize import normalize
from .gradient import gradient
import math as m
import os
from .insideout import insideout



class twoinfall(double_exponential):
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

	def __init__(self, radius, dt = 0.01, dr = 0.1, 
			**kwargs):

		kwargs["tau2"] = insideout.timescale(radius)

		super().__init__(**kwargs)

		self.norm *= normalize(self, gradient, radius, dt=dt, dr=dr)
