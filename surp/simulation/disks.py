r"""
The diskmodel objects employed in the Johnson et al. (2021) study.
"""

try:
	ModuleNotFoundError
except NameError:
	ModuleNotFoundError = ImportError
try:
	import vice
except (ModuleNotFoundError, ImportError):
	raise ModuleNotFoundError("Could not import VICE.")
if vice.version[:2] < (1, 2):
	raise RuntimeError("""VICE version >= 1.2.0 is required to produce \
Johnson et al. (2021) figures. Current: %s""" % (vice.__version__))
else: pass


from vice.toolkit import hydrodisk
from .._globals import END_TIME, MAX_SF_RADIUS
from . import migration
from . import models
from .models.utils import get_bin_number, interpolate
from .models.gradient import gradient
import math as m
import sys


class diskmodel(vice.milkyway):

	r"""
	A milkyway object tuned to the Johnson et al. (2021) models specifically.

	Parameters
	----------
	zone_width : ``float`` [default : 0.1]
		The width of each annulus in kpc.
	name : ``str`` [default : "diskmodel"]
		The name of the model; the output will be stored in a directory under
		this name with a ".vice" extension.
	spec : ``str`` [default : "static"]
		A keyword denoting the time-dependence of the star formation history.
		Allowed values:

		- "static"
		- "insideout"
		- "lateburst"
		- "outerburst"
        - "twoexp"
        - "threeexp"

	verbose : ``bool`` [default : True]
		Whether or not the run the models with verbose output.
	migration_mode : ``str`` [default : "diffusion"]
		A keyword denoting the time-dependence of stellar migration.
		Allowed values:

		- "diffusion"
		- "linear"
		- "sudden"
		- "post-process"

	kwargs : varying types
		Other keyword arguments to pass ``vice.milkyway``.

	Attributes and functionality are inherited from ``vice.milkyway``.
	"""

	def __init__(self, zone_width = 0.1, name = "diskmodel", spec = "static",
		verbose = False, migration_mode = "diffusion", **kwargs):
		super().__init__(zone_width = zone_width, name = name,
			verbose = verbose, **kwargs)
		self.migration_mode = migration_mode
		self.calculate_nstars()
		self.evolution = star_formation_history(spec = spec,
			zone_width = zone_width)
		self.mode = "sfr"

	def calculate_nstars(self):
		if self.zone_width <= 0.2 and self.dt <= 0.02 and self.n_stars >= 6:
			Nstars = 3102519
		else:
			Nstars = 2 * int(MAX_SF_RADIUS / self.zone_width * END_TIME / self.dt *
							self.n_stars)

		print("N stars=%i" % Nstars)
		self.migration.stars = migration.diskmigration(self.annuli,
				N = Nstars, mode = self.migration_mode,
				filename = "%s_analogdata.out" % (self.name))

	def run(self, *args, **kwargs):
		out = super().run(*args, **kwargs)
		self.migration.stars.close_file()
		return out

	@classmethod
	def from_config(cls, config, **kwargs):
		r"""
		Obtain a ``diskmodel`` object with the parameters encoded into a
		``config`` object.

		**Signature**: diskmodel.from_config(config, **kwargs)

		Parameters
		----------
		config : ``config``
			The ``config`` object with the parameters encoded as attributes.
			See src/simulations/config.py.
		**kwargs : varying types
			Additional keyword arguments to pass to ``diskmodel.__init__``.

		Returns
		-------
		model : ``diskmodel``
			The ``diskmodel`` object with the proper settings.
		"""
				# bug here, needs passed n_stars
		model = cls(zone_width = config.zone_width,**kwargs)
		model.n_stars = config.star_particle_density
		model.dt = config.timestep_size
		model.bins = config.bins
		model.elements = config.elements
		model.setup_nthreads = config.setup_nthreads
		model.nthreads = config.nthreads
		model.calculate_nstars()
		return model
