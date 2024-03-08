from dataclasses import dataclass, field, asdict
from .._globals import END_TIME
import json
from vice.milkyway.milkyway import _get_radial_bins
import numpy as np



@dataclass
class MWParams:
    """
    Parameters
    ----------
    filename: ``str``
        The name of the model

    save_dir: ``str`` [default: None]
        The directory to save the model in
        If None, then use the argument passed to this script

    eta: ``float`` [default: 1]
        The prefactor for mass-loading strength

    agb_model: ``str`` [default: C11]
        The AGB model to use for yields. 
        - C11
        - K10 
        - V13
        - K16
        - A: Custom analytic model, see ``surp/yields.py``
        
    timestep: ``float`` [default: 0.01]
        The timestep of the simulation, measured in Gyr.
        Decreasing this value can significantly speed up results

    yield_kwargs: dict 
        kwargs passed to set_yields in ``surp/yields.py``

    migration_mode: ``str``
        Default value: diffusion
        The migration mode for the simulation. 
        Can be one of diffusion (most physical), linear, post-process, ???

        The star formation specification. 
        Accepable values are
        - "insideout"
        - "constant"
        - "lateburst"
        - "outerburst"
        - "twoexp"
        - "threeexp"
        see vice.migration.src.simulation.disks.star_formation_history

    n_stars: ``int`` [default: 2]
        The number of stars to create during each timestep of the model.

    yield_scale: ``float`` [default: 1]
        A factor by which to reduce the model's outflows. 
    """
    filename:str = "milkyway"

    yield_scale:float = 1
    r:float = 0.4
    timestep:float = 0.02
    n_stars:int = 1
    migration_mode:str = "diffusion"
    migration:str = "gaussian"
    verbose:bool = False
    sigma_R:bool = True
    sf_law:str = "J21"
    zone_width:float = 0.1

    RIa:str = "plaw"

    sfh_model:str = "insideout"
    sfh_kwargs:dict = field(default_factory=dict)
    max_sf_radius:float = 15.5 # Radius in kpc beyond which the SFR = 0

    thin_disk_scale_radius:float = 2.5 # kpc
    thick_disk_scale_radius:float = 2.0 # kpc
    thin_to_thick_ratio:float = 0.27 # at r = 0

    # Stellar mass of Milky Way (Licquia & Newman 2015, ApJ, 806, 96)
    M_star_MW:float = 5.17e10

    save_migration:bool = False

    # calculated
    N_star_tot:int = 0 # calculated by model
    simple:bool = False
    mode:str = "sfr"

    def __post_init__(self):
        self.process()

    def process(self):
        if self.migration_mode == "post-process":
            self.simple = True
            self.migration_mode = "diffusion"

        if self.sfh_model in ["twoinfall", "conroy22"]:
            self.mode = "ifr"

        self.calc_N_stars_tot()

    @property
    def radial_bins(self):
        return _get_radial_bins(self.zone_width)

    @property
    def times(self):
        return np.arange(0, END_TIME, self.timestep)

    def calc_N_stars_tot(self):
        Nstars = int(2*self.max_sf_radius/self.zone_width * END_TIME/self.timestep * self.n_stars)

        N_MAX = 3_102_519 # max num stars for hydrodisk
        if self.migration == "hydrodisk" and Nstars > N_MAX:
            Nstars = N_MAX

        self.N_star_tot = Nstars

        return Nstars

    def to_dict(self):
        return asdict(self)

    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)


    @classmethod
    def from_file(cls, filename):
        with open(filename, "r") as f:
            params = json.load(f)
        return cls(**params)
