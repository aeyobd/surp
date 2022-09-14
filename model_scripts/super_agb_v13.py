from multizone_sim import run_model
import vice


if __name__ == "__main__":
    run_model("super_agb_v13", n_stars=2, agb_yields = "ventura13", agb_factor=10, migration_mode="diffusion", n_yields="J22")
