import numpy as np

from .._globals import END_TIME
from surp.utils import AbstractParams

from vice.milkyway.milkyway import _get_radial_bins


class MWParams(AbstractParams):
    """
    MWParams(kwargs...)
    MWParams.from_file(filename)

    A struct storing the parameters to surp.create_model with. 

    Parameters
    ----------

    ## VICE parameters

    filename: ``str``
        The name of the model (outputed to filename.vice). 

    zone_width: ``float`` 
        The width of each zone in vice

    timestep: ``float``
        The timestep of the simulation, measured in Gyr.

    n_stars: ``int``
        The number of stars to create during each timestep in each zone of the model.

    verbose: ``bool``
        Whether to print out the progress of the model

    simple: ``bool``
        Use a simple migration model. Also set to True if migration_mode is "post-process"

    smoothing: ``string``
        See vice documentation. 

    imf: ``string``
        Initial mass function. May be kroupa, salpeter, or chabrier

    RIa: ``string``
        The SNeIa delay time distribution. May be "exp" or "plaw"

    t_d_ia: ``float``
        The delay time of type Ia supernovae in Gyr

    tau_ia: ``float``
        The timescale of type Ia supernovae in Gyr

    m_upper: ``float``
        The upper mass limit of the IMF

    m_lower: ``float``
        The lower mass limit of the IMF

    migration_mode: ``str``
        The migration mode to use. Only matters if migration = "hydrodisk", 
        Options are
        - "diffusion"
        - "post-process"

    N_star_tot: ``int``
        The total number of stars to create in the model. 
        Only matters if migration = "hydrodisk"
        If left as default (-1), it will be calculated based on the other parameters.

    mode: ``str=""``
        The mode of the model. Can be sfr, ifr, or gas. 
        If left as default (""), it will be set depending on the sf_model.

    ## Additional parameters


    migration: ``str``
        The migration mode to use. Options are
        - "hydrodisk"
        - "gaussian"
        - "rand_walk"

    sigma_R: ``bool``
        Strength of migration for random walk migration (and TODO gaussian...)

    save_migration: ``bool``
        If true, writes the migration history to the file star_migration.dat.


    sfh_model: ``str``
        The star formation specification. 
        Accepable values are
        - "insideout"
        - "constant"
        - "lateburst"
        - "twoexp"
        - "threeexp"
        - "twoinfall" (also changes ...)

    sfh_kwargs: ``dict``
        kwargs passed to surp.simulation.star_formation_history....

    max_sf_radius: ``float``
        The radius in kpc beyond which the SFR = 0

    Re: ``float``
        The scale radius of the galaxy. Used to apply Sanchez star formation.

    sf_law: ``string``
        The star formation law to use. 
        - "J21"
        - "conroy"
        - "twoinfall"

    tau_star0: ``float``
        The star formation timescale at t=0 for J21 sf_law.

    M_star_MW: ``float``
        The stellar mass of Milky Way. Used to normalize SFH.

    thin_disk_scale_radius: ``float``
        The scale radius of the thin disk in kpc

    thick_disk_scale_radius: ``float``
        The scale radius of the thick disk in kpc

    thin_to_thick_ratio: ``float``
        The ratio of the thin to thick disk surface density at r = 0kpc, not solar radius

    r_sun: ``float``
        The distance of the sun from the galactic center in kpc.
        Used for twoinfall model only to calculate thin/thick ratio at solar postion.

    MH_grad_R0: ``float``
        Transition radius for the metallicity gradient

    MH_grad_MH0: ``float``
        Metallicity at the transition radius

    MH_grad_in: ``float``
        Metallicity gradient inside the transition radius

    MH_grad_out: ``float``
        Metallicity gradient outside the transition radius

    eta_scale: ``float``
        additional factor which to multiply y_mg by when setting outflow scale. Increases outflows appropriately

    r: ``float``
        Estimate of the return fraction for normalizing the stellar gradient
        and mass loading.

    tau_star_sfh_grad: ``float``
        The scale factor on tau_star/tau_sfh*R term used for the gradient (i.e. approximation of tau_star/tau_sfh ~ R).
        Likely should be zero.

    seed: ``int`` = 0
        The random number seed.

    
    Attributes
    ---------------------
        
    radial_bins: ``list``
        The radial bins for the model.

    times: ``np.ndarray``
        The time for each timestep for the model.


    Methods
    -------
    process(): 
        processes the model after it has been created

    save(filename): 
        saves the model

    to_dict(): 
        returns a dictionary of the model

    calc_N_stars_tot(): 
        calculates the total number of stars to create

    """

    filename:str

    zone_width:float
    timestep:float
    n_stars:int

    simple:bool
    verbose:bool

    migration_mode:str
    migration:str
    sigma_R:float
    save_migration:bool

    smoothing:float

    imf:str
    t_d_ia:float
    RIa:str
    tau_ia:float
    m_upper:float
    m_lower:float

    sfh_model:str
    sfh_kwargs:dict
    max_sf_radius:float
    Re:float

    sf_law:str
    tau_star0:float

    M_star_MW:float
    thin_disk_scale_radius:float
    thick_disk_scale_radius:float
    thin_to_thick_ratio:float

    r_sun:float


    # outflow settings
    MH_grad_R0:float
    MH_grad_MH0:float
    MH_grad_in:float
    MH_grad_out:float
    eta_scale:float
    r:float
    tau_star_sfh_grad: float

    seed:int = 0

    # calculated live
    N_star_tot:int = -1
    mode:str = ""


    def __post_init__(self):
        self.process()


    def process(self):
        """
        Processes the model after it has been created. 
        Sets simple, migration_mode, and mode if they are not set.
        """
        if self.migration_mode == "post-process":
            self.simple = True
            self.migration_mode = "diffusion"

        if self.mode == "":
            if self.sfh_model in ["twoinfall", "conroy22"]:
                self.mode = "ifr"
            else:
                self.mode = "sfr"

        if self.N_star_tot == -1:
            self.calc_N_stars_tot()


    def calc_N_stars_tot(self):
        """Calculates the total number of stars if using hydrodisk migration"""

        N_MAX = 3_102_519 # max num stars for hydrodisk

        Nstars = int(2*self.max_sf_radius/self.zone_width 
                     * END_TIME/self.timestep * self.n_stars)

        if self.migration == "hydrodisk" and Nstars > N_MAX:
            Nstars = N_MAX

        self.N_star_tot = Nstars

        return Nstars


    @property
    def radial_bins(self):
        """Returns the radial bins for the model"""
        return _get_radial_bins(self.zone_width)


    @property
    def times(self):
        """Returns the time for each timestep for the model"""
        return np.arange(0, END_TIME, self.timestep)

