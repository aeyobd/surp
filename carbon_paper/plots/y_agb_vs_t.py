import arya
import matplotlib.pyplot as plt
import vice
import surp

import sys 
sys.path.append("..")
from yield_plot_utils import AGB_MODELS, AGB_LABELS, agb_interpolator, plot_ssp_time


def make_plot():
    plt.figure(figsize=(10/3, 10/3))

    vice.yields.ccsne.settings["c"] = 0
    vice.yields.sneia.settings["c"] = 0
    vice.yields.ccsne.settings["fe"] = 0
    vice.yields.agb.settings["fe"] = surp.yield_models.ZeroAGB()


    for i in range(4):
        model = AGB_MODELS[i]
        vice.yields.agb.settings["c"] = agb_interpolator("c", study=model)
        times, y = plot_ssp_time(Z=surp.gce_math.MH_to_Z(-0.1), label=AGB_LABELS[model])
      
        
    plt.text(3, 0.7, "SNe Ia Fe", rotation=42, color="k")
    plot_ssp_time("fe", color="k", ls="--", zorder=-1)


    plt.ylim(-0.3, 1.2)
    plt.xlim(0.03, 13.2)
    plt.xticks([0.1, 1, 10], labels=[0.1, 1, 10])
    plt.ylabel("cumulative AGB C production (normalized)")
    plt.xlabel("time / Gyr")
    arya.Legend(color_only=True)

    plt.savefig("figures/y_agb_vs_t.pdf")


if __name__ == "__main__":
    with open("figures/y_agb_vs_t.txt", "w") as sys.stdout:
        make_plot()
