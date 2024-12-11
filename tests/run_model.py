import surp
import vice
import os
import numpy as np

if __name__ == "__main__":
    MODEL = vice.milkyway()
    MODEL.dt = 0.1
    MODEL.verbose = True

    MODEL.smoothing = 0.4

    MODEL.run((np.arange(0, 13, 0.1)))

    print("finished")

