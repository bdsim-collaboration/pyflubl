from ._usrbin import *
from ._usrdump import *
import numpy as _np

from matplotlib import pyplot as _plt

def plot(data):
    if type(data) == Usrbin :
        pass
    elif type(data) == Usrdump :
        plot_usrdump(data)

def plot_usrdump(ud):
    for t in ud.track_data :
        _plt.plot([t[0],t[3]],
                  [t[2],t[5]],"+")

    #_plt.show()

def plot_usrbin(ub, detector_idx = 0, projection = 0):
    if type(projection) == int:
        if projection == 0 :
            str_projection = ""
        elif projection == 1 :
            str_projection = ""
        elif projection == 2 :
            str_projection = ""

    detector_projection = ub.detector[detector_idx].data.sum(projection)

    _plt.imshow(_np.log10(detector_projection))
