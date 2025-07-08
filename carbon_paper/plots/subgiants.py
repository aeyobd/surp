import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patheffects
from surp import subgiants
import seaborn as sns

import arya
import sys
sys.path.append("..")
import mw_model_plots


fig, axs = plt.subplots(1, 2, figsize=(7, 10/3), sharey=True, gridspec_kw={"wspace": 0}, dpi=250)


kwargs = dict(
    rasterized=True, ec="none", s=1
)

plt.sca(axs[0])
sns.scatterplot(subgiants, x="MG_H", y="C_MG", hue="high_alpha", **kwargs)

mw_model_plots.zooh_models({}, [],  zorder=3, errorbar=None)

L = arya.Legend(labels=[r"low $\alpha$", r"high $\alpha$"], color_only=True, loc=4)
# for text in L.mpl_leg.get_texts():
#     text.set_path_effects([mpl.patheffects.Stroke(linewidth=0, foreground='w'),
#                        mpl.patheffects.Normal()])
    
plt.ylabel("[C/Mg]")
plt.xlabel("[Mg/H]")
plt.xlim(-0.5, 0.5)
plt.ylim(-0.45, 0.15)

plt.sca(axs[1])
sns.scatterplot(subgiants, x="MG_FE", y="C_MG", hue="MG_H", hue_norm=(-0.5, 0.5), legend=False,  palette=plt.get_cmap(), **kwargs)

mw_model_plots.zofeo_models({}, [], zorder=3,  errorbar=None)


plt.xlim(-0.08, 0.45)

plt.xlabel("[Mg/Fe]")

cax = axs[1].inset_axes([1.05, 0., 0.05, 1])

arya.Colorbar(clim=(-0.5, 0.5), label="[Mg/H]", cax=cax)
plt.savefig("figures/subgiants.pdf")
