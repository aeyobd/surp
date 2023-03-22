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
# https://gka.github.io/palettes/#/256|s|2b2f57,a24d9b,ff5345,f4d15a|ffffe0,ff005e,93003a|1|1

cmap = ['#2b2f57', '#2c2f58', '#2e3058', '#2f3059', '#30305a', '#31315a',
        '#33315b', '#34315b', '#35325c', '#37325c', '#38325d', '#39335e',
        '#3a335e', '#3c335f', '#3d345f', '#3e3460', '#403460', '#413561',
        '#423561', '#433562', '#453662', '#463663', '#473663', '#483664',
        '#4a3764', '#4b3765', '#4c3765', '#4e3866', '#4f3866', '#503867',
        '#513967', '#533968', '#543968', '#553a68', '#563a69', '#583a69',
        '#593a6a', '#5a3b6a', '#5c3b6a', '#5d3b6b', '#5e3c6b', '#5f3c6b',
        '#613c6c', '#623c6c', '#633d6c', '#653d6d', '#663d6d', '#673e6d',
        '#683e6e', '#6a3e6e', '#6b3f6e', '#6c3f6e', '#6d3f6f', '#6f406f',
        '#70406f', '#71406f', '#734070', '#744170', '#754170', '#764170',
        '#784270', '#794271', '#7a4271', '#7b4371', '#7d4371', '#7e4371',
        '#7f4471', '#804471', '#824472', '#834472', '#844572', '#854572',
        '#874572', '#884672', '#894672', '#8a4672', '#8b4772', '#8d4772',
        '#8e4872', '#8f4872', '#904873', '#924973', '#934973', '#944973',
        '#954a73', '#964a73', '#984a73', '#994b73', '#9a4b73', '#9b4b73',
        '#9c4c72', '#9e4c72', '#9f4d72', '#a04d72', '#a14d72', '#a24e72',
        '#a34e72', '#a54f72', '#a64f72', '#a75072', '#a85072', '#a95072',
        '#aa5172', '#ab5171', '#ac5271', '#ad5271', '#af5371', '#b05371',
        '#b15471', '#b25471', '#b35470', '#b45570', '#b55570', '#b65670',
        '#b75670', '#b85770', '#b9586f', '#ba586f', '#bb596f', '#bc596f',
        '#bd5a6f', '#be5a6e', '#bf5b6e', '#c05b6e', '#c15c6e', '#c25c6e',
        '#c35d6d', '#c45e6d', '#c55e6d', '#c65f6d', '#c75f6c', '#c8606c',
        '#c9616c', '#ca616c', '#cb626b', '#cc626b', '#cd636b', '#cd646b',
        '#ce646a', '#cf656a', '#d0666a', '#d1666a', '#d26769', '#d36869',
        '#d36869', '#d46968', '#d56a68', '#d66b68', '#d76b68', '#d76c67',
        '#d86d67', '#d96d67', '#da6e67', '#da6f66', '#db7066', '#dc7066',
        '#dd7165', '#dd7265', '#de7365', '#df7465', '#df7464', '#e07564',
        '#e17664', '#e17763', '#e27863', '#e37863', '#e37963', '#e47a62',
        '#e57b62', '#e57c62', '#e67c62', '#e67d61', '#e77e61', '#e77f61',
        '#e88060', '#e98160', '#e98260', '#ea8360', '#ea835f', '#eb845f',
        '#eb855f', '#ec865f', '#ec875e', '#ed885e', '#ed895e', '#ed8a5e',
        '#ee8b5d', '#ee8c5d', '#ef8c5d', '#ef8d5d', '#f08e5c', '#f08f5c',
        '#f0905c', '#f1915c', '#f1925c', '#f1935b', '#f2945b', '#f2955b',
        '#f2965b', '#f3975b', '#f3985a', '#f3995a', '#f39a5a', '#f49b5a',
        '#f49c5a', '#f49d5a', '#f59e59', '#f59f59', '#f5a059', '#f5a159',
        '#f5a259', '#f6a359', '#f6a459', '#f6a558', '#f6a658', '#f6a758',
        '#f6a858', '#f7a958', '#f7aa58', '#f7ab58', '#f7ac58', '#f7ad58',
        '#f7ae58', '#f7af58', '#f7b058', '#f7b158', '#f7b258', '#f7b357',
        '#f7b457', '#f7b557', '#f7b657', '#f7b757', '#f7b857', '#f7b957',
        '#f7bb58', '#f7bc58', '#f7bd58', '#f7be58', '#f7bf58', '#f7c058',
        '#f7c158', '#f7c258', '#f7c358', '#f6c458', '#f6c558', '#f6c658',
        '#f6c758', '#f6c859', '#f6c959', '#f5cb59', '#f5cc59', '#f5cd59',
        '#f5ce59', '#f5cf5a', '#f4d05a', '#f4d15a']

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
