from ._usrbin import *
from ._usrdump import *
import numpy as _np

from pyg4ometry.transformation import matrix2tbxyz as _matrix2tbxyz

from matplotlib import pyplot as _plt
from matplotlib import patches as _patches

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

def plot_machine(machine) :
    m = machine

    for eidx in range(0,len(m.sequence),1) :
        ename  = m.sequence[eidx]
        e = m.elements[ename]

        x, y, z = [1000*v for v in m.midint[eidx]]
        xr, yr, zr  = _matrix2tbxyz(_np.array(m.midrotationint[eidx]))

        print(z,y,z,xr,yr,zr)

        length  = e.length
        width = 250

        ###########################################
        ax = _plt.subplot(3,1,1)
        _plt.plot(z,x,"+")
        bounding_box = _makeBoundingRect([z,x], [length*1000, width], yr)
        ax.add_patch(bounding_box)

        _plt.xlabel("z/mm")
        _plt.ylabel("x/mm")

        ###########################################
        ax = _plt.subplot(3,1,2)
        _plt.plot(z, y,"+")
        bounding_box = _makeBoundingRect([z,y], [length*1000, width], xr)
        ax.add_patch(bounding_box)

        _plt.xlabel("z/mm")
        _plt.ylabel("y/mm")

        ###########################################
        ax = _plt.subplot(3,1,3)
        _plt.plot(x, y,"+")
        bounding_box = _makeBoundingRect([x,y], [width, width], zr)
        ax.add_patch(bounding_box)

        _plt.xlabel("x/mm")
        _plt.ylabel("y/mm")

        ###########################################
        _plt.tight_layout()

def _makeBoundingRect(centre, size, angle) :
    cen = _np.array(centre)
    size  = _np.array(size)
    rr = _np.array([[_np.cos(angle), -_np.sin(angle)],
                    [_np.sin(angle),  _np.cos(angle)]])
    ll = cen - rr @ size/2

    return  _patches.Rectangle(ll, size[0], size[1],
                               angle=angle / _np.pi * 180, fill=False)

