from dataclasses import dataclass
from .._globals import END_TIME



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

    spec: ``str`` [default: "insideout"]
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


    burst_size: ``float`` [default: 1.5]
        The size of the SFH burst for lateburst model.

    eta_factor: ``float`` [default: 1]
        A factor by which to reduce the model's outflows. 
    """
    filename:str = "milkyway"

    yield_scale:float = 1
    r:float = 0.4
    timestep:float = 0.02
    n_stars:int = 1
    migration_mode = "diffusion"
    migration = "gaussian"
    verbose:bool = False
    sigma_R:bool = True
    sf_law:str = "J21"
    zone_width:float = 0.1

    RIa:str = "plaw"
    sfh_model:str = "insideout"
    sfh_tau1:float = None
    sfh_A1:float = None
    sfh_tau2:float = None
    sfh_A2:float = None
    sfh_tau3:float = None
    sfh_A3:float = None
    sfh_t1:float = None
    sfh_t2:float = None
    tau_rise: float = 2

    max_sf_radius:float = 15.5 # Radius in kpc beyond which the SFR = 0

    thin_disk_scale_radius:float = 2.5 # kpc
    thick_disk_scale_radius:float = 2.0 # kpc
    thin_to_thick_ratio:float = 0.27 # at r = 0

    # Stellar mass of Milky Way (Licquia & Newman 2015, ApJ, 806, 96)
    M_star_MW:float = 5.17e10
    N_star_tot:int = 0

    def process(self):
        if self.migration_mode == "post-process":
            self.simple = True
            self.migration_mode = "diffusion"
        else:
            self.simple = False

        if self.sfh_model == "twoinfall" or self.sfh_model == "conroy22":
            self.mode = "ifr"
        else:
            self.mode = "sfr"

        self.calc_N_stars_tot()


    def calc_N_stars_tot(self):
        N_MAX = 3_102_519
        Nstars = int(2*self.max_sf_radius/self.zone_width * END_TIME/self.timestep * self.n_stars)
        if self.migration_mode not in ["rand_walk", "gaussian"] and Nstars > N_MAX:
            Nstars = N_MAX
        self.N_star_tot = Nstars

        return Nstars
