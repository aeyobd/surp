import numpy as np
from vice.milkyway.milkyway import _get_radial_bins

from .._globals import END_TIME
from surp.utils import AbstractParams



class MWParams(AbstractParams):
    """
    MWParams(kwargs...)
    MWParams.from_file(filename)

    A struct storing the parameters to surp.create_model with. 


    Parameters
    ----------
    filename: ``str``
        The name of the model (outputed to filename.vice). 

    zone_width: ``float`` 
        The width of each zone in vice

    timestep: ``float``
        The timestep of the simulation, measured in Gyr.

    n_stars: ``int``
        The number of stars to create during each timestep in each zone of the model.

    sfh_model: ``str``
        Can be one of diffusion (most physical), linear, post-process, ???

        The star formation specification. 
        Accepable values are
        - "insideout"
        - "constant"
        - "lateburst"
        - "outerburst"
        - "twoexp"
        - "threeexp"

    sf_law: ``string``
        The star formation law to use. May be "J21" or "K13"

    n_stars: ``int``
        The number of stars to create during each timestep of the model.

    verbose: ``bool``
        Whether to print out the progress of the model

    migration_mode: ``str``
        The migration mode to use. Options are
        - "diffusion"
        - "post-process"

    migration: ``str``
        The migration mode to use. Options are
        - "hydrodisk"
        - "gaussian"
        - "random_walk"

    simple: ``bool``
        Use a simple migration mode

    sigma_R: ``bool``
        Strength of migration for gaussian and random walk migration

    save_migration: ``bool``
        If true, writes the migration history to a file

    smoothing: ``string``
        See vice documentation. 

    imf: ``string``
        Initial mass function. May be kroupa, salpeter
        or (TODO chabrier)

    m_upper: ``float``
        The upper mass limit of the IMF

    m_lower: ``float``
        The lower mass limit of the IMF

    RIa: ``string``
        The SNeIa delay time distribution. May be "exp" or "plaw"

    t_d_ia: ``float``
        The delay time of type Ia supernovae in Gyr

    tau_ia: ``float``
        The timescale of type Ia supernovae in Gyr

    sf_law: ``string``
        The star formation law to use. 
        - "J21"
        - "C22"
        - "twoinfall"

    Re: ``float``
        The scale radius of the galaxy

    sfh_model: ``string``
        The star formation history model to use. Implemented are
        - "insideout"
        - "lateburst"
        - "constant"
        - "twoinfall"

    sfh_kwargs: ``dict``
        kwargs passed to surp.simulation.star_formation_history....

    max_sf_radius: ``float``
        The radius in kpc beyond which the SFR = 0

    mode:str = "" # updated depending on sfh_model


    M_star_MW: ``float``
        The stellar mass of Milky Way (Licquia & Newman 2015, ApJ, 806, 96)

    thin_disk_scale_radius: ``float``
        The scale radius of the thin disk in kpc

    thick_disk_scale_radius: ``float``
        The scale radius of the thick disk in kpc

    thin_to_thick_ratio: ``float``
        The ratio of the thin to thick disk surface density at r = 0kpc, not solar radius

    r_sun: ``float``
        The distance of the sun from the galactic center in kpc

    # TODO: outflow go to kwargs...

    # outflow settings
    MH_grad_R0:float
    MH_grad_MH0:float
    MH_grad_in:float
    MH_grad_out:float
    eta_scale: ``float``
        additional factor which to multiply y_mg by when setting outflow scale. Increases outflows appropriately

    r:float # TODO determine
    tau_star_sfh_grad: float # TODO Determine this

    
    Calculated Parameters / Attributes
    ---------------------
    N_star_tot:int = -1 # calculated by model
        
    radial_bins
    times


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

    n_stars:int
    simple:bool
    verbose:bool

    migration_mode:str
    migration:str
    sigma_R:float
    save_migration:bool

    imf:str

    timestep:float
    t_d_ia:float
    RIa:str
    smoothing:float
    tau_ia:float
    m_upper:float
    m_lower:float


    sf_law:str
    Re:float

    sfh_model:str
    sfh_kwargs:dict
    max_sf_radius:float

    # Stellar mass of Milky Way (Licquia & Newman 2015, ApJ, 806, 96)
    M_star_MW:float

    thin_disk_scale_radius:float
    thick_disk_scale_radius:float
    thin_to_thick_ratio:float

    r_sun:float # kpc, GRAVITY Collaboration 2018


    # outflow settings
    MH_grad_R0:float
    MH_grad_MH0:float
    MH_grad_in:float
    MH_grad_out:float
    eta_scale:float
    r:float # TODO determine
    tau_star_sfh_grad: float # TODO Determine this


    # calculated live
    N_star_tot:int = -1 # calculated by model
    mode:str = "" # updated depending on sfh_model


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

