from multizone_sim import run_model
import vice


if __name__ == "__main__":
    run_model("super_agb_k16", n_stars=2, agb_yields = "karakas16", agb_factor=10, migration_mode="diffusion", n_yields="J22")
