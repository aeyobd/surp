from dataclasses import dataclass, field, asdict
from .._globals import END_TIME
import json
from vice.milkyway.milkyway import _get_radial_bins
import numpy as np



@dataclass
class MWParams:
    """
    MWParams(kwargs...)
    MWParams.from_file(filename)

    A struct storing the parameters to surp.create_model with.

    Parameters
    ----------
    filename: ``str``
        The name of the model

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

    n_stars: ``int`` [default: 2]
        The number of stars to create during each timestep of the model.

    sf_law: ``string`` [default: "J21"]
        The star formation law to use. May be "J21" or "K13"

    Parameters directly passed to vice
    -----------------------------------
    timestep: ``float`` [default: 0.01]
        The timestep of the simulation, measured in Gyr.
        Decreasing this value can significantly speed up results
    zone_width: ``float`` [default: 0.1]

    eta_scale: ``float`` [default: 1.0]
        additional factor which to multiply y_mg by when setting outflow scale. Increases outflows appropriately

    imf: ``string`` [default: "kroupa"]
        Initial mass function. May be kroupa, salpeter (vice)
        or todo (chabrier)

    m_upper: ``float`` [default: 100]
        The upper mass limit of the IMF
        
    m_lower: ``float`` [default: 0.08]
        The lower mass limit of the IMF

    Re: ``float`` [default: 5]
        The scale radius of the galaxy in kpc

    Attributes
    ----------
    radial_bins
    times


    Methods
    -------
    save(filename): saves the model
    to_dict(): returns a dictionary of the model
    process(): processes the model after it has been created
    calc_N_stars_tot(): calculates the total number of stars to create

    """

    filename:str = "milkyway"
    zone_width:float = 0.1

    n_stars:int = 1
    simple:bool = False
    verbose:bool = False
    N_star_tot:int = -1 # calculated by model

    migration_mode:str = "diffusion"
    migration:str = "gaussian"
    sigma_R:bool = True
    save_migration:bool = False

    mode:str = "" # updated depending on sfh_model
    imf:str = "kroupa"

    timestep:float = 0.02
    t_d_ia:float = 0.15
    RIa:str = "plaw"
    smoothing:str = 0
    tau_ia:str = 1.5
    m_upper:float = 100
    m_lower:float = 0.08


    sf_law:str = "J21"
    Re:float = 5

    # sfh settings
    sfh_model:str = "insideout"
    sfh_kwargs:dict = field(default_factory=lambda: dict(tau_sfh="sanchez", tau_rise=2))
    max_sf_radius:float = 15.5 # Radius in kpc beyond which the SFR = 0

    # Stellar mass of Milky Way (Licquia & Newman 2015, ApJ, 806, 96)
    M_star_MW:float = 5.17e10

    thin_disk_scale_radius:float = 2.5 # kpc
    thick_disk_scale_radius:float = 2.0 # kpc
    thin_to_thick_ratio:float = 3.70 # at r = 0kpc, not solar radius

    r_sun:float = 8.122 # kpc, GRAVITY Collaboration 2018


    # outflow settings
    MH_grad_R0:float = 5
    MH_grad_MH0:float = 0.29 
    MH_grad_in:float = -0.015
    MH_grad_out:float = -0.09
    eta_scale:float = 1.0
    r:float = 0.4 # TODO determine
    tau_star_sfh_grad: float = 0 # TODO Determine this


    @classmethod
    def from_file(cls, filename):
        with open(filename, "r") as f:
            params = json.load(f)
        return cls(**params)


    def __post_init__(self):
        self.process()


    def process(self):
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
        N_MAX = 3_102_519 # max num stars for hydrodisk

        Nstars = int(2*self.max_sf_radius/self.zone_width 
                     * END_TIME/self.timestep * self.n_stars)

        if self.migration == "hydrodisk" and Nstars > N_MAX:
            Nstars = N_MAX

        self.N_star_tot = Nstars

        return Nstars


    def to_dict(self):
        return asdict(self)


    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)


    @property
    def radial_bins(self):
        return _get_radial_bins(self.zone_width)

    @property
    def times(self):
        return np.arange(0, END_TIME, self.timestep)

