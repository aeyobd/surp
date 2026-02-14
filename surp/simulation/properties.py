import numpy as np

import vice

try:
    from vice.toolkit.rand_walk.rand_walk_stars import rand_walk_stars 
    from vice.toolkit.analytic_migration.analytic_migration_2d import analytic_migration_2d
    from vice.toolkit.analytic_migration.migration_models import final_positions_gaussian_py
except ImportError:
    print("Daniel's vice fork not installed, analytic/gaussian migration not available")

from vice.toolkit.hydrodisk.hydrodiskstars import hydrodiskstars 
from vice.toolkit import J21_sf_law

from .star_formation_history import star_formation_history 
from ..yields import set_yields
from .._globals import Z_SUN
from surp.yield_models import chabrier


def create_migration(bins, params):
    """
    create_migration(bins, params)

    Create the migration object for the model galaxy.

    Depends on 
    - params.migration: the type of migration to use
    - params.save_migration: whether to save the migration data 
    - params.n_stars: the number of stars to produce per timestep (gaussian and
        random walk)
    - params.timestep: the timestep of the model
    - params.verbose: whether to print verbose output (gaussian only)
    - params.seed: the seed for the migration (gaussian only)
    - params.N_star_tot: the total number of stars in the model (hydrodisk only)
    """
    kind = params.migration
    if params.save_migration:
        filename=params.filename + "_star_migration.dat"
    else:
        filename = None

    if kind == "rand_walk":
        migration = rand_walk_stars(bins, n_stars=params.n_stars, dt=params.timestep, 
            name=filename, **params.migration_kwargs
            )
    elif kind == "gaussian":
        final_positions = final_positions_gaussian_py(
                seed=params.seed, 
                **params.migration_kwargs
            )
        migration = analytic_migration_2d(
            bins, 
            dt=params.timestep, 
            n_stars=params.n_stars, 
            filename=filename, 
            verbose=params.verbose,
            initial_final_filename="migration_initial_final.dat",
            seed=params.seed,
            final_positions=final_positions,
            migration_mode=params.migration_mode,
        )
    elif kind == "hydrodisk":
        migration = diskmigration(bins, N=params.N_star_tot,
                mode=params.migration_mode, filename=filename)
    else:
        raise ValueError("migration mode not known", kind)

    return migration


def set_sf_law(model, params):
    """
    set_sf_law(model, params)

    Set the star formation law for the model galaxy for each zone.

    Depends on
    - params.sf_law: the star formation law to use. Options are "conroy22",
      "twoinfall", "J21"
    - params.tau_star0: the present day molecular gas depletion time (J21 only)

    Additionally for params.sf_law = "twoinfall":
    - params.sfh_kwargs: the parameters for the twoinfall model. Uses 
    nu1, nu2, t2 to set the sfh model.

    """
    for zone in model.zones:
       zone.Mg0 = 0.
    
    tot_area = 0  # sanity check for me

    for i in range(model.n_zones):
        R1 = model.annuli[i]
        R2 = model.annuli[i+1]
        R = (R1 + R2)/2
        area = np.pi * (R2**2 - R1**2)
        tot_area += area

        if params.sf_law == "conroy22":
            model.zones[i].tau_star = conroy_sf_law(area, **params.sf_law_kwargs)
        elif params.sf_law == "twoinfall":
            model.zones[i].tau_star = twoinfall_sf_law(area,
                **params.sf_law_kwargs
                )
        elif params.sf_law == "J21":
            model.zones[i].tau_star = J21_sf_law(area, mode=params.mode, 
                    **params.sf_law_kwargs
                )
        else:
            raise ValueError("SF law not known ", params.sf_law)

    tot_area_exp = np.pi * (model.annuli[-1]**2 - model.annuli[0]**2)
    relerr = abs(tot_area - tot_area_exp) / tot_area_exp
    assert relerr < 1e-3, f"Area {tot_area} does not match expected {tot_area_exp} within 1e-3"



def conroy_tau_star(t):
    if t < 2.5:
        tau_st = 50
    elif 2.5 <= t < 3.7:
        tau_st = 50/(1+3*(t-2.5))**2
    else:
        tau_st = 2.36
    return tau_st

def liam_RIa(t, W=1, alpha=-1.1):
    """
    liam_RIa()

    The recommended SN Ia DTD from Dubay et al 2024. 

    ... Dubay LO, Johnson JA, Johnson JW. 2024. Astrophys. J. 973:55
    """


    if t < W:
        return 1
    else:
        return (t/W)**alpha



class conroy_sf_law:
    r"""
    conroy_sf_law()

    Creates a callable class returning the star formation timescale at time t
    for the Conroy et al. 2022[1] model.

    .. math:: \tau_{\star} = \begin{cases} 50 & t < 2.5 \\ \frac{50}{(1+3(t-2.5))^2} & 2.5 \leq t < 3.7 \\ 2.36 & t \geq 3.7 \end{cases}

    
    [^1]: Conroy, C., et al. 2022, arXiv:2202.02989
    """
    def __init__(self, area=None):
        self.area = area

    def __call__(self, t):
        tau_st = conroy_tau_star(t)
        return tau_st

    def __str__(self):
        return "Conroy22"


class twoinfall_sf_law:
    """
    twoinfall_tau_star(t2, nu1, nu2)

    Returns the star formation timescale at time t for a two-infall model.

    Parameters
    ----------
    t2: time of transition
    nu1: star formation efficienty before transition
    nu2: star formation efficiency after transition
    """
    def __init__(self, area=None, *, t2=4.1, nu1=2, nu2=1):
        self.area = area
        self.t2 = t2
        self.nu1 = nu1
        self.nu2 = nu2

    def __call__(self, t):
        if t < self.t2:
            tau_st = 1/self.nu1
        else:
            tau_st = 1/self.nu2
        return tau_st

    def __str__(self):
        return f"Two-infall SF law, t2={self.t2}, nu1={self.nu1}, nu2={self.nu2}"

    




class MH_grad:
    def __init__(self, params):
        """Metallicity gradient of galaxy from Hayden et al. 2014.

        Depends on
        - params.MH_grad_R0: the transition radius of the gradient.
        - params.MH_grad_MH0: the metallicity at R0
        - params.MH_grad_in: the gradient inside the solar radius
        - params.MH_grad_out: the gradient outside the solar radius
        """
        self.R0 = params.MH_grad_R0
        self.MH_0 = params.MH_grad_MH0
        self.zeta_in = params.MH_grad_in
        self.zeta_out = params.MH_grad_out

    def __call__(self, R):
        return self.MH_0 + (R-self.R0) * np.where(R<self.R0, self.zeta_in, self.zeta_out)

    def __str__(self):
        s =  f"{self.MH_0:0.2f} + {self.zeta_in}(R-{self.R0}) , R > {self.R0}"
        s += "; "
        s +=  f"{self.MH_0:0.2f} + {self.zeta_out}(R-{self.R0}) , R < {self.R0}"
        return s


class mass_loading:
    """A class which represents the mass loading profile of galaxy. Set yields before calling this

    Depends on
    - params.eta_scale: scales the assumed yield setting used here.
      approximantly multiplies eta by this value
    - params.r: is the approximated return fraction
    - params.tau_star_sfh_grad: is the linear approximation of tau_star / tau_sfh ~ R.
    and additional parameter sent to MH_grad. 

    Since the gradient tends to be slightly underproduced where
    tau_star/tau_sfh would be highest (inner galaxy) where eta->0, this is best
    simply set to zero.
    """
    def __init__(self, params):
        r = params.r
        yo = vice.yields.ccsne.settings["o"] * params.eta_scale

        self.B = params.r - 1
        self.C = yo / vice.solar_z("o") 

        self.MH_func = MH_grad(params)
        self.tau_star_sfh_grad = params.tau_star_sfh_grad

    def __call__(self, R_gal):
        MH = self.MH_func(R_gal)
        eta = self.B + self.C * 10**-MH + self.tau_star_sfh_grad * R_gal
        return np.maximum(0, eta)

    def __str__(self):
        s = f"{self.B:0.4f} + {self.C:0.4f}×10^[M/H];\r\t\t\t [M/H] = {self.MH_func}"
        return s

    def __repr__(self):
        return str(self)


def get_imf(params):
    """return the IMF for the model galaxy based on the parameters.
    Only supports salpeter, kroupa, chabrier. 

    Depends on
    - params.imf: the IMF to use
    """
    if params.imf == "salpeter":
        return params.imf
    elif params.imf == "kroupa":
        return params.imf
    elif params.imf == "chabrier":
        return chabrier
    else:
        raise ValueError("IMF not known", params.imf)





class diskmigration(hydrodiskstars):

	r"""
	A ``hydrodiskstars`` object which writes extra analog star particle data to
	an output file.

	Parameters
	----------
	radbins : array-like
		The bins in galactocentric radius in kpc corresponding to each annulus.
	mode : ``str`` [default : "linear"]
		A keyword denoting the time-dependence of stellar migration.
		Allowed values:

		- "diffusion"
		- "linear"
		- "sudden"
		- "post-process"

	filename : ``str`` [default : "stars.out"]
		The name of the file to write the extra star particle data to.

	Attributes
	----------
	write : ``bool`` [default : False] 	
		A boolean describing whether or not to write to an output file when
		the object is called. The ``multizone`` object, and by extension the
		``milkyway`` object, automatically switch this attribute to True at the
		correct time to record extra data.
	"""

	def __init__(self, radbins, mode = "diffusion", filename = "stars.out",
		**kwargs):
		super().__init__(radbins, mode = mode, **kwargs)
		if isinstance(filename, str):
			self._file = open(filename, 'w')
			self._file.write("# zone_origin\ttime_origin\tanalog_id\tzfinal\n")
		else:
			raise TypeError("Filename must be a string. Got: %s" % (
				type(filename)))

		# use only disk stars in these simulations
		self.decomp_filter([1, 2])

		# Multizone object automatically swaps this to True in setting up
		# its stellar population zone histories
		self.write = False

	def __call__(self, zone, tform, time):
		if tform == time:
			super().__call__(zone, tform, time) # reset analog star particle
			if self.write:
				if self.analog_index == -1:
					# finalz = 100
					finalz = 0
					analog_id = -1
				else:
					finalz = self.analog_data["zfinal"][self.analog_index]
					analog_id = self.analog_data["id"][self.analog_index]
				self._file.write("%d\t%.2f\t%d\t%.2f\n" % (zone, tform,
					analog_id, finalz))
			else: pass
			return zone
		else:
			return super().__call__(zone, tform, time)

	def close_file(self):
		r"""
		Closes the output file - should be called after the multizone model
		simulation runs.
		"""
		self._file.close()

	@property
	def write(self):
		r"""
		Type : bool

		Whether or not to write out to the extra star particle data output
		file. For internal use by the vice.multizone object only.
		"""
		return self._write

	@write.setter
	def write(self, value):
		if isinstance(value, bool):
			self._write = value
		else:
			raise TypeError("Must be a boolean. Got: %s" % (type(value)))
