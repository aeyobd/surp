import matplotlib as mpl
# the smallest plot elements should be 0.3pt \approx 0.1mm
# for a paper, we want fonts 10/12/14

colors = ['#0173b2', '#de8f05', '#029e73', '#d55e00', '#cc78bc', 
          '#ca9161', '#fbafe4', '#949494', '#ece133', '#56b4e9']
markers = ['o', '+', '^', '*', 's', 
           'd', 'o', 'x', '1']
fill =    [True,  True,  True,  True,
           False, False, False, False]


def init():
    mpl.style.use("./journal.mplstyle")
    # style.use('seaborn-colorblind')
    mpl.ticker.AutoLocator.__init__ = AutoLocatorInit

# override default tick locator to avoid 2.5 ticks
def AutoLocatorInit(self):
    mpl.ticker.MaxNLocator.__init__(self,
            nbins = "auto",
            steps = [1,2,5,10])


init()

# locator for linear scales but with log variables (0.2, 0.3, 0.5, and 1 are preferred step sizes)
