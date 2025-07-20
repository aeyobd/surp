import pandas as pd
import matplotlib.pyplot as plt
import surp

import surp.gce_math as gcem
import arya
import vice
import numpy as np

from mcmc_setup import results, yagb_props
from surp.agb_interpolator import interpolator as agb_interpolator


y_z0 = lambda z: 1e-3
y_z1 = np.vectorize(lambda z: 1*y_z0(z) + surp.yield_models.Lin_CC(slope=0.001 / surp.Z_SUN, y0=0)(z))

M_H=np.linspace(-0.5, 0.5, 1000)
Z = gcem.MH_to_Z(M_H)
surp.set_yields(verbose=False)
ys_fiducial = surp.yields.calc_y(Z)

Y_agbs = {
    "fruity": agb_interpolator("c"),
    "fiducial": agb_interpolator("c"),
    "fruity_mf0.7": agb_interpolator("c", mass_factor=0.7),
    "aton": agb_interpolator("c", study="ventura13"),
    "monash": agb_interpolator("c", study="karakas16"),
    "nugrid": agb_interpolator("c", study="pignatari16"),
    "analytic": surp.yield_models.C_AGB_Model(y0=1e-3, zeta=1e-3, tau_agb=1, t_D=0.15)
}


Z = gcem.MH_to_Z(M_H)
y_agbs = {}
for key, Y_agb in Y_agbs.items():
    vice.yields.agb.settings["c"] = Y_agb
    ys_a = surp.yields.calc_y(Z, kind="agb")
    
    y_agbs[key] = ys_a




def plot_y_tot(result, ys_a, thin=10, M_H=M_H, color="black", alpha=None):
    samples = result.samples
    Z = gcem.MH_to_Z(M_H)
    if alpha is None:
        alpha = 1 / len(samples)**(1/3) / 10
        
    ys_z0 = y_z0(Z)
    ys_z1 = y_z1(Z)
    ymg = vice.yields.ccsne.settings["mg"]

    for i, sample in samples[::thin].iterrows():
        yt = sample.y0_cc * ys_z0 + sample.zeta_cc * ys_z1 + sample.alpha * ys_a
        plt.plot(M_H, yt / ymg, color=color, alpha=alpha, rasterized=True)
    




def plot_y_tot_mean(result, ys_a, M_H=M_H, y_z0=y_z0, y_z1=y_z1, **kwargs):
    samples = result.samples
    Z = gcem.MH_to_Z(M_H)
        
    ys_z0 = y_z0(Z)
    ys_z1 = y_z1(Z)
    ymg = vice.yields.ccsne.settings["mg"]

    sample = samples.median()
    yt = sample.y0_cc * ys_z0 + sample.alpha * ys_a
    if "zeta_cc" in sample.keys():
        yt += sample.zeta_cc * ys_z1
    if "A_cc" in sample.keys():
        yt += sample.A_cc * ys_z2 
        
    plt.plot(M_H, yt / ymg, **kwargs)






plot_labels = {
    "fiducial": r"FRUITY+gas-phase",
    "fruity": r"FRUITY",
    "aton": r"ATON",
    "monash": r"Monash",
    "nugrid": r"NuGrid",
    "fruity_mf0.7": r"FRUITY m0.7",
}



plt.figure()
plot_y_tot(results["fiducial"], y_agbs["fruity"], thin=100, alpha=0.01, color=arya.COLORS[0])

for i, (key, label) in enumerate(plot_labels.items()): 
    result = results[key]
    if key in y_agbs.keys():
        y_agb = y_agbs[key]
    else:
        print("warning, no agb for ", key)
        
        y_agb = y_agbs["analytic"]

    
    plot_y_tot_mean(result, y_agb, color=arya.COLORS[i], label=label, ls=["-", ":", "--", "-."][i%4])
    

plt.xlabel(r"$\log Z / Z_\odot$")
plt.ylabel(r"$y_{\rm C} / y_{\rm Mg}$")

plt.legend()
plt.savefig("figures/mcmc_y_tot.pdf")

