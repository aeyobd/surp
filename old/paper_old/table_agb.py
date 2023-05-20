import vice

def setup():
    vice.yields.ccsne.settings["c"] = 0
    vice.yields.sneia.settings["c"] = 0

def y_c_0(study):
    vice.yields.agb.settings["c"] = study
    return vice.single_stellar_population("c", mstar=1, Z=0.014,
                                          time=15)[0][-1]

def alpha(study):
    y_c = 0.005
    frac = 0.2
    y_c_agb = y_c * frac

    return y_c_agb/y_c_0(study)

setup()

for study in ["cristallo11", "karakas10", "ventura13", "karakas16"]:
    print(f"{study}\t{y_c_0(study):0.6f}\t{alpha(study):4.2f}")



