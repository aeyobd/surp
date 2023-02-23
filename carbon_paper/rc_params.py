import matplotlib as mpl
import matplotlib.style as style 

# Need to pick a colorblind friendly color palate
# style.use('seaborn-colorblind')



style.use("./journal.mplstyle")
# # font sizes
# SMALL_SIZE = 8
# MEDIUM_SIZE = 10
# BIGGER_SIZE = 12




# # Text parameters
# mpl.rcParams["font.family"] = "serif"
# mpl.rcParams["text.usetex"] = True
# mpl.rcParams["mathtext.fontset"] = "custom"
# mpl.rcParams["text.latex.preamble"] = r"""
# \usepackage{amsmath}
# \usepackage{newtxtext,newtxmath}
# \usepackage[T1]{fontenc}
# """

# # font sizes
# mpl.rcParams["figure.titlesize"] = BIGGER_SIZE
# mpl.rcParams["axes.titlesize"] = SMALL_SIZE
# mpl.rcParams["axes.labelsize"] = BIGGER_SIZE
# mpl.rcParams["xtick.labelsize"] = MEDIUM_SIZE
# mpl.rcParams["ytick.labelsize"] = MEDIUM_SIZE
# mpl.rcParams["legend.fontsize"] = MEDIUM_SIZE
# mpl.rcParams["font.size"] = SMALL_SIZE

# # Figure formatting

# default_width = 3.15 # in = 80 mm
# mpl.rcParams["figure.figsize"] = (default_width, default_width)
# mpl.rcParams["figure.facecolor"] = "white"
# mpl.rcParams["figure.dpi"] = 200

# # Error bars and legend formatting
# mpl.rcParams["errorbar.capsize"] = 2.5

# mpl.rcParams["legend.numpoints"] = 1
# mpl.rcParams["legend.frameon"] = False
# mpl.rcParams["legend.handletextpad"] = 0.3

# # Axes and tick formatting
# mpl.rcParams["axes.linewidth"] = 0.8
# mpl.rcParams["xtick.direction"] = "in"
# mpl.rcParams["ytick.direction"] = "in"
# mpl.rcParams["ytick.right"] = True
# mpl.rcParams["xtick.top"] = True
# mpl.rcParams["xtick.minor.visible"] = True
# mpl.rcParams["ytick.minor.visible"] = True

# mpl.rcParams["xtick.major.size"] = 4
# mpl.rcParams["ytick.major.size"] = 4

# mpl.rcParams["xtick.minor.size"] = 2
# mpl.rcParams["ytick.minor.size"] = 2

# mpl.rcParams["xtick.major.width"] = 0.8
# mpl.rcParams["ytick.major.width"] = 0.8

# mpl.rcParams["xtick.minor.width"] = 0.4
# mpl.rcParams["ytick.minor.width"] = 0.4

# mpl.rcParams["axes.unicode_minus"] = False

# # lines and markers
# mpl.rcParams["lines.linewidth"] = 0.8
# mpl.rcParams["lines.markersize"] = 3

# mpl.rcParams['axes.prop_cycle'] = \
#     mpl.cycler(color=['#0173b2',
#                   '#de8f05',
#                   '#029e73',
#                   '#d55e00',
#                   '#cc78bc',
#                   '#ca9161',
#                   '#fbafe4',
#                   '#949494',
#                   '#ece133',
#                   '#56b4e9'])