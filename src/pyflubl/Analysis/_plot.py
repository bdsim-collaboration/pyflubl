from ._usrbin import *
from ._usrdump import *
import numpy as _np
from matplotlib.colors import LogNorm as _LogNorm

from pyg4ometry.transformation import matrix2tbxyz as _matrix2tbxyz

from matplotlib import pyplot as _plt
from matplotlib import patches as _patches
import matplotlib.transforms as _transforms

def plot(data):
    if type(data) == Usrbin :
        pass
    elif type(data) == Usrdump :
        plot_usrdump(data)

def plot_usrdump(ud, projection = "xz", linewidth=1):
    if projection == "xz":
        for t in ud.track_data :
            _plt.plot([10*t[2],10*t[5]], [10*t[0],10*t[3]],
                      color=(0.5, 0.5, 0.5),
                      linewidth=linewidth)

    if projection == "":
        for t in ud.track_data :
            _plt.plot([10*t[2],10*t[5]], [10*t[0],10*t[3]],linewidth=linewidth)

    #_plt.show()

def plot_usrbin(ub, detector_idx = 0, projection = 0, cmap = "Greens",
                rotmatrix = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                translation = _np.array([0,0,0]),
                bookkeeping = None ):
    if type(projection) == int:
        if projection == 0 :
            str_projection = ""
        elif projection == 1 :
            str_projection = ""
        elif projection == 2 :
            str_projection = ""

    if bookkeeping :
        rotmatrix = bookkeeping['usrbinnumber_usrbininfo'][detector_idx]["rotation"]
        translation = bookkeeping['usrbinnumber_usrbininfo'][detector_idx]["translation"]

    vp = _np.array(rotmatrix) @ _np.array([0, 0, 1])
    yr = _np.arctan2(vp[0], vp[2])

    ax = _plt.gca()
    trans = _transforms.Affine2D().rotate_deg(yr/_np.pi*180).translate(translation[2], translation[0]) + ax.transData

    detector = ub.detector[detector_idx]
    detector_projection = detector.data.sum(projection)

    # TODO the extend depends on the projection
    _plt.imshow(detector_projection, extent=[detector.e3low*10, detector.e3high*10,
                detector.e1high*10, detector.e1low*10],
                norm=_LogNorm(),
                transform=trans,
                cmap=cmap)

def plot_machine(machine) :
    m = machine

    for eidx in range(0,len(m.sequence),1) :
        ename  = m.sequence[eidx]
        e = m.elements[ename]

        x, y, z = [1000*v for v in m.midint[eidx]]
        xr, yr, zr  = _matrix2tbxyz(_np.array(m.midrotationint[eidx]))

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

def plot_machine_xz(machine) :
    m = machine

    for eidx in range(0,len(m.sequence),1) :
        ename  = m.sequence[eidx]
        e = m.elements[ename]

        x, y, z = [1000*v for v in m.midint[eidx]]
        vp = _np.array(m.midrotationint[eidx]) @ _np.array([0,0,1])

        yr1 = _np.arctan2(vp[0], vp[2])

        xr, yr, zr = _matrix2tbxyz(_np.array(m.midrotationint[eidx]))

        length  = e.length
        width = 250

        ###########################################
        ax = _plt.subplot(1,1,1)
        _plt.plot(z,x,"+", color=(0,0,1.0))
        bounding_box = _makeBoundingRect([z,x], [length*1000, width], yr1)
        ax.add_patch(bounding_box)

        _plt.xlabel("z/mm")
        _plt.ylabel("x/mm")

        _plt.tight_layout()

def _makeBoundingRect(centre, size, angle) :
    cen = _np.array(centre)
    size  = _np.array(size)
    rr = _np.array([[_np.cos(angle), -_np.sin(angle)],
                    [_np.sin(angle),  _np.cos(angle)]])
    ll = cen - rr @ size/2

    return  _patches.Rectangle(ll, size[0], size[1],
                               angle=angle / _np.pi * 180, fill=False,
                               color=(1.0,0,0))

