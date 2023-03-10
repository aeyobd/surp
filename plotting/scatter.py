import matplotlib.pyplot as plt

class Scatter:
    def __init__(self, plot, x, y, **kwargs):
        plot._ax.scatter(x, y, **kwargs)

