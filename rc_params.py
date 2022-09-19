import matplotlib as mpl
import matplotlib.style as style
style.use('seaborn-colorblind')

# Text parameters
mpl.rcParams["font.family"] = "serif"
mpl.rcParams["text.usetex"] = True
mpl.rcParams["mathtext.fontset"] = "custom"
mpl.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}"
mpl.rcParams["figure.titlesize"] = 18
mpl.rcParams["axes.titlesize"] = 18
mpl.rcParams["axes.labelsize"] = 20
mpl.rcParams["xtick.labelsize"] = 18
mpl.rcParams["ytick.labelsize"] = 18
mpl.rcParams["legend.fontsize"] = 18

mpl.rcParams["font.size"] = 18

# Figure formatting
mpl.rcParams["figure.figsize"] = (5, 5)
mpl.rcParams["figure.facecolor"] = "white"

# Error bars and legend formatting
mpl.rcParams["errorbar.capsize"] = 5
mpl.rcParams["legend.numpoints"] = 1
mpl.rcParams["legend.frameon"] = False
mpl.rcParams["legend.handletextpad"] = 0.3

# Axes and tick formatting
mpl.rcParams["axes.linewidth"] = 1
mpl.rcParams["xtick.direction"] = "in"
mpl.rcParams["ytick.direction"] = "in"
mpl.rcParams["ytick.right"] = True
mpl.rcParams["xtick.top"] = True
mpl.rcParams["xtick.minor.visible"] = True
mpl.rcParams["ytick.minor.visible"] = True
mpl.rcParams["xtick.major.size"] = 10
mpl.rcParams["ytick.major.size"] = 10
mpl.rcParams["xtick.minor.size"] = 5
mpl.rcParams["ytick.minor.size"] = 5
mpl.rcParams["xtick.major.width"] = 0.5
mpl.rcParams["ytick.major.width"] = 0.5
mpl.rcParams["xtick.minor.width"] = 0.5
mpl.rcParams["ytick.minor.width"] = 0.5

mpl.rcParams["axes.unicode_minus"] = False
