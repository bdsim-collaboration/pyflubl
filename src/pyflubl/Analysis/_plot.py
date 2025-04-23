from ._usrbin import *
from ._usrdump import *

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