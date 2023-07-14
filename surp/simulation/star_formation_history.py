from . import models
from .._globals import ZONE_WIDTH, MAX_SF_RADIUS
from .models.utils import get_bin_number, interpolate
from .models.gradient import gradient




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

	def __init__(self, spec = "static", **kwargs):
		self._radii = []
		self._evol = []
		i = 0
		self._spec = spec
		max_radius = 20 # kpc, defined by ``vice.milkyway`` object.
		while (i + 1) * ZONE_WIDTH < max_radius:
			self._radii.append((i + 0.5) * ZONE_WIDTH)
			self._evol.append({
					"static":		models.static,
					"insideout":	models.insideout,
					"lateburst":	models.lateburst,
					"outerburst":	models.outerburst,
					"twoexp":	models.twoexp,
					"twoinfall":	models.twoinfall,
					"threeexp":	models.threeexp,
				}[spec.lower()]((i + 0.5) * ZONE_WIDTH, **kwargs))
			i += 1

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
		return f"{self._spec}"

	def __repr__(self):
		return str(self)

