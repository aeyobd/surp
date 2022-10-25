from multizone_sim import run_model


if __name__ == "__main__":
    run_model("lateburst", agb_yields="cristallo11", n_yields="J22", spec="lateburst", burst_size=2.5)
