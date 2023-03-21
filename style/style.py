import matplotlib as mpl
import os
# the smallest plot elements should be 0.3pt \approx 0.1mm
# for a paper, we want fonts 10/12/14

COLORS = ['#648FFF', '#DC267F', '#FFB000', '#785EF0', '#FE6100']

COLORS = ['#0173b2', '#de8f05', '#029e73', '#d55e00', '#cc78bc', 
          '#ca9161', '#fbafe4', '#949494', '#ece133', '#56b4e9']

MARKERS = ['o', '+', '^', '*', 's', 
           'd', 'o', 'x', '1']
FILL =    [True,  True,  True,  True,
           False, False, False, False]


# pallate c.o chroma.jl palette helper
cmap = ['#271d50', '#291d51', '#2a1d51', '#2c1e52', '#2d1e52', '#2f1e53',
        '#301e53', '#321f54', '#331f54', '#351f55', '#361f55', '#371f56',
        '#392056', '#3a2057', '#3c2057', '#3d2058', '#3f2158', '#402159',
        '#412159', '#43215a', '#44215a', '#45225b', '#47225b', '#48225c',
        '#4a225c', '#4b235d', '#4c235d', '#4e235d', '#4f235e', '#50235e',
        '#52245f', '#53245f', '#542460', '#562460', '#572460', '#582561',
        '#5a2561', '#5b2561', '#5c2562', '#5e2662', '#5f2663', '#602663',
        '#622663', '#632764', '#642764', '#662764', '#672765', '#682865',
        '#6a2865', '#6b2866', '#6c2866', '#6e2866', '#6f2966', '#702967',
        '#722967', '#732a67', '#742a68', '#752a68', '#772a68', '#782b68',
        '#792b69', '#7b2b69', '#7c2b69', '#7d2c69', '#7e2c69', '#802c6a',
        '#812d6a', '#822d6a', '#842d6a', '#852d6a', '#862e6b', '#872e6b',
        '#892e6b', '#8a2f6b', '#8b2f6b', '#8d2f6b', '#8e306c', '#8f306c',
        '#90306c', '#92316c', '#93316c', '#94316c', '#96326c', '#97326c',
        '#98326c', '#99336c', '#9b336d', '#9c336d', '#9d346d', '#9e346d',
        '#a0346d', '#a1356d', '#a2356d', '#a3366d', '#a5366d', '#a6366d',
        '#a7376d', '#a8376d', '#aa386d', '#ab386d', '#ac386d', '#ad396d',
        '#ae396c', '#b03a6c', '#b13a6c', '#b23b6c', '#b33b6c', '#b53c6c',
        '#b63c6c', '#b73c6c', '#b83d6c', '#b93d6c', '#bb3e6b', '#bc3e6b',
        '#bd3f6b', '#be3f6b', '#c0406b', '#c1406b', '#c2416a', '#c3416a',
        '#c4426a', '#c5426a', '#c74369', '#c84369', '#c94469', '#ca4568',
        '#cb4667', '#cc4765', '#cc4864', '#cd4963', '#ce4a62', '#cf4c61',
        '#cf4d60', '#d04e5f', '#d14f5e', '#d1505d', '#d2515c', '#d3525b',
        '#d3535b', '#d4545a', '#d55659', '#d55758', '#d65857', '#d65957',
        '#d75a56', '#d75b55', '#d85c55', '#d85e54', '#d95f53', '#d96053',
        '#da6152', '#da6252', '#db6351', '#db6551', '#db6650', '#dc6750',
        '#dc684f', '#dd694f', '#dd6a4e', '#dd6b4e', '#de6d4e', '#de6e4d',
        '#de6f4d', '#df704d', '#df714c', '#df724c', '#e0744c', '#e0754c',
        '#e0764b', '#e0774b', '#e1784b', '#e1794b', '#e17b4b', '#e17c4b',
        '#e27d4a', '#e27e4a', '#e27f4a', '#e2804a', '#e2824a', '#e3834a',
        '#e3844a', '#e3854a', '#e3864a', '#e3874a', '#e3894a', '#e38a4b',
        '#e38b4b', '#e48c4b', '#e48d4b', '#e48e4b', '#e4904b', '#e4914c',
        '#e4924c', '#e4934c', '#e4944c', '#e4954d', '#e4964d', '#e4984d',
        '#e4994d', '#e49a4e', '#e49b4e', '#e49c4f', '#e49d4f', '#e49f4f',
        '#e4a050', '#e4a150', '#e4a251', '#e4a351', '#e4a452', '#e4a652',
        '#e3a753', '#e3a853', '#e3a954', '#e3aa54', '#e3ab55', '#e3ad56',
        '#e3ae56', '#e2af57', '#e2b057', '#e2b158', '#e2b259', '#e2b459',
        '#e1b55a', '#e1b65b', '#e1b75c', '#e1b85c', '#e0b95d', '#e0bb5e',
        '#e0bc5f', '#dfbd5f', '#dfbe60', '#dfbf61', '#dec062', '#dec163',
        '#dec364', '#ddc465', '#ddc565', '#ddc666', '#dcc767', '#dcc968',
        '#dbca69', '#dbcb6a', '#dbcc6b', '#dacd6c', '#dace6d', '#d9cf6e',
        '#d9d16f', '#d8d270', '#d7d371', '#d7d472', '#d6d573', '#d6d674',
        '#d5d875', '#d5d977', '#d4da78', '#d3db79']


def to_rgb(h):
    return tuple(int(h[i:i+2], 16)/256 for i in (1, 3, 5))

def get_cmap():
    cmap_rgb = [to_rgb(h) for h in cmap]
    ca =  mpl.colors.ListedColormap(cmap_rgb)
    ca.set_under(cmap_rgb[0])
    ca.set_over(cmap_rgb[-1])
    return ca


def init():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    style = "journal"

    path = os.path.join(dir_path, style + ".mplstyle")
    mpl.style.use(path)
    # style.use('seaborn-colorblind')
    mpl.ticker.AutoLocator.__init__ = AutoLocatorInit
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color = COLORS)

# override default tick locator to avoid 2.5 ticks
def AutoLocatorInit(self):
    mpl.ticker.MaxNLocator.__init__(self,
            nbins = "auto",
            steps = [1,2,5,10])

FIG_SIZE = (2.362, 2.362)

init()

# locator for linear scales but with log variables (0.2, 0.3, 0.5, and 1 are preferred step sizes)
