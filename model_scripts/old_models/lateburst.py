from multizone_sim import run_model


if __name__ == "__main__":
    #run_model("fiducial", agb_yields="cristallo11", n_stars=8)
    run_model("lateburst", agb_yields="cristallo11", n_yields="J22", spec="lateburst")