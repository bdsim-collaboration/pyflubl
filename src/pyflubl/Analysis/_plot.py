from ._usrbin import *
from ._usrdump import *
from ..Coordinates import Coordinates as _Coordinates

import numpy as _np
from matplotlib.colors import LogNorm as _LogNorm

from pyg4ometry.transformation import matrix2tbxyz as _matrix2tbxyz

from matplotlib import pyplot as _plt
from matplotlib import patches as _patches
import matplotlib.transforms as _transforms

def _sort_clockwise(points):
    """points: (N, 2) array"""
    cx, cy = points.mean(axis=0)
    angles = _np.arctan2(points[:,1] - cy, points[:,0] - cx)
    return points[_np.argsort(-angles)]

def plot(data):
    if type(data) == Usrbin :
        pass
    elif type(data) == Usrdump :
        plot_usrdump(data)

def plot_usrdump(ud, projection = "xz", linewidth=1, markersize=1):

    if projection == "xz":
        axis1 = 0
        axis2 = 2
    elif projection == "zx":
        axis1 = 2
        axis2 = 0
    elif projection == "xy" :
        axis1 = 0
        axis2 = 1
    elif projection == "yx" :
        axis1 = 1
        axis2 = 0
    elif projection == "yz" :
        axis1 = 1
        axis2 = 2
    elif projection == "zy" :
        axis1 = 2
        axis2 = 1
    else :
        raise ValueError("projection must be xz, yz, xy or zx, yz, yx")

    for t in ud.track_data :
        _plt.plot([10*t[axis1],10*t[axis1+3]], [10*t[axis2],10*t[axis2+3]],
                  "-",
                  color=(1.0, 0, 0),
                  linewidth=linewidth)
        _plt.plot([10*t[axis1],10*t[axis1+3]], [10*t[axis2],10*t[axis2+3]],
                  "o",
                  markersize=markersize,
                  color=(0, 0, 0))

def plot_usrbin_projection_xarray(xarr3d,
                                  projection = "zx",
                                  rotation_matrix = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                                  translation_vector = _np.array([0,0,0]),
                                  cmap = "Greens") :
    if projection == "zx" :
        proj = xarr3d.sum(dim="y")
        zmin = xarr3d.coords['z'].min()
        zmax = xarr3d.coords['z'].max()
        xmin = xarr3d.coords['x'].min()
        xmax = xarr3d.coords['x'].max()

        vp = _np.array(rotation_matrix) @ _np.array([0, 0, 1])
        yr = _np.arctan2(vp[0], vp[2])
        translation_vector= [translation_vector[2], translation_vector[0]]

        #print(f'rotation_angle={yr}, translation_vector={translation_vector}')
        plot_usrbin_projection_numpy(proj.to_numpy(),
                                     extent=[zmin, zmax, xmax, xmin],
                                     rotation_angle=yr,
                                     translation_vector=translation_vector,
                                     cmap=cmap)
    elif projection == "zy" :
        proj = xarr3d.sum(dim="x")
        zmin = xarr3d.coords['z'].min()
        zmax = xarr3d.coords['z'].max()
        ymin = xarr3d.coords['y'].min()
        ymax = xarr3d.coords['y'].max()

        vp = _np.array(rotation_matrix) @ _np.array([0, 0, 1])
        xr = _np.arctan2(vp[1], vp[2])
        translation_vector= [translation_vector[2], translation_vector[1]]

        #print(f'rotation_angle={xr}, translation_vector={translation_vector}')
        plot_usrbin_projection_numpy(proj.to_numpy(),
                                     extent=[zmin, zmax, ymax, ymin],
                                     rotation_angle=xr,
                                     translation_vector=translation_vector,
                                     cmap=cmap)
    elif projection == "xy" :
        proj = xarr3d.sum(dim="z")
        xmin = xarr3d.coords['x'].min()
        xmax = xarr3d.coords['x'].max()
        ymin = xarr3d.coords['y'].min()
        ymax = xarr3d.coords['y'].max()

        vp = _np.array(rotation_matrix) @ _np.array([1, 0, 0])
        zr = _np.arctan2(vp[1], vp[0])
        translation_vector= [translation_vector[0], translation_vector[1]]

        #print(f'rotation_angle={zr}, translation_vector={translation_vector}')
        plot_usrbin_projection_numpy(proj.to_numpy(),
                                     extent=[xmin, xmax, ymin, ymax],
                                     rotation_angle=zr,
                                     translation_vector=translation_vector,
                                     cmap=cmap)
    else :
        print("projection does not exist yet, please implement")


def plot_usrbin_projection_numpy(arr2d,
                                 extent = [-1.,1.,-1.,1.],
                                 rotation_angle = 0,
                                 translation_vector = [0.,0.],
                                 cmap = "Greens") :

    # upgrade to numpy array
    translation_vector = _np.array(translation_vector)

    # calculate transformation for imshow
    ax = _plt.gca()
    trans = _transforms.Affine2D().rotate_deg(rotation_angle/_np.pi*180).translate(translation_vector[0], translation_vector[1]) + ax.transData

    # plot imshow
    _plt.imshow(arr2d,
                extent=extent,
                norm=_LogNorm(),
                transform=trans,
                cmap=cmap)


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
        _xg, _yg, _zg = [1000*v for v in m.midgeomint[eidx]]
        _xe, _ye, _ze = [1000*v for v in m.endint[eidx]]
        _xeg, _yeg, _zeg = [1000*v for v in m.endgeomint[eidx]]

        xr, yr, zr  = _matrix2tbxyz(_np.array(m.midrotationint[eidx]))

        length  = e.length
        width = 300

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

        x, y, z       = [1000*v for v in m.midint[eidx]]
        xg, yg, zg    = [1000*v for v in m.midgeomint[eidx]]
        xe, ye, ze    = [1000*v for v in m.endint[eidx]]
        xeg, yeg, zeg = [1000*v for v in m.endgeomint[eidx]]

        vp = _np.array(m.midrotationint[eidx]) @ _np.array([0,0,1])

        yr1 = _np.arctan2(vp[0], vp[2])

        xr, yr, zr = _matrix2tbxyz(_np.array(m.midrotationint[eidx]))

        length  = e.length
        width = 250

        ###########################################
        ax = _plt.subplot(1,1,1)
        _plt.plot(z,x,"+", color=(0,0,1))
        _plt.plot(zg,xg,"x", color=(0,1,0))
        _plt.plot(ze,xe,"+", color=(1,0,0))
        _plt.plot(zeg,xeg,"x", color=(1,1,0))

        bounding_box = _makeBoundingRect([zg,xg], [length*1000, width], yr1)
        if e.category == "drift" :
            bounding_box = _makeBoundingTrap([zg,xg], [length*1000, width], yr1,
                                             facecolor="green")
        elif e.category == "rbend" :
            bounding_box = _makeBoundingTrap([zg,xg], [length*1000, width], yr1,
                                             facecolor="blue")
        elif e.category == "sbend" :
            angle = e['angle']
            chord = 2 * (length / angle) * _np.sin(angle / 2)
            bounding_box = _makeBoundingTrap([zg,xg], [chord*1000, width], yr1, e1=angle/2, e2=angle/2,
                                             facecolor="blue")
        elif e.category == "quadrupole" :
            bounding_box = _makeBoundingTrap([zg,xg], [length*1000, width], yr1,
                                             facecolor="red")

        ax.add_patch(bounding_box)

        _plt.xlabel("z/mm")
        _plt.ylabel("x/mm")

        _plt.tight_layout()

def plot_coordinates(coordinates) :
    _plt.subplot(2,2,1)
    plot_coordinates_projection(coordinates, projection = "xz")

    _plt.subplot(2,2,2)
    plot_coordinates_projection(coordinates, projection = "yz")

    _plt.subplot(2,2,3)
    plot_coordinates_projection(coordinates, projection = "xy")

    _plt.tight_layout()

def plot_coordinates_projection(coordinates,
                                projection = "zx",
                                plotCoordinateMarkers = True,
                                plotFilledElements = True,
                                plotNormals = True) :

    fig, ax = _plt.subplots(figsize=(7, 3.5))

    if projection == "xz":
        axis1 = 0
        axis2 = 2
    elif projection == "zx":
        axis1 = 2
        axis2 = 0
    elif projection == "xy" :
        axis1 = 0
        axis2 = 1
    elif projection == "yx" :
        axis1 = 1
        axis2 = 0
    elif projection == "yz" :
        axis1 = 1
        axis2 = 2
    elif projection == "zy" :
        axis1 = 2
        axis2 = 1
    else :
        raise ValueError("Invalid projection",projection)

    if type(coordinates) == str :
        coordinates_new = _Coordinates()
        coordinates_new.LoadJSON(coordinates)
        coordinates = coordinates_new

    for i in range(0,len(coordinates),1) :
        length = coordinates.element_chord_length[i]*1000

        vp = _np.array(coordinates.rot_mid[i]) @ _np.array([0,0,1])
        yr = _np.arctan2(vp[axis2], vp[axis1])

        ast = coordinates.arc_sta[i]*1000
        am = coordinates.arc_mid[i]*1000
        ae = coordinates.arc_end[i]*1000

        cs = coordinates.cho_sta[i]*1000
        cm = coordinates.cho_mid[i]*1000
        ce = coordinates.cho_end[i]*1000

        fi = coordinates.fac_sta[i]
        fe = coordinates.fac_end[i]

        bp = coordinates.tra[i]*1000

        if plotCoordinateMarkers :
            markersize = 1.0
        else :
            markersize = 0.0

        _plt.plot(ast[axis1],ast[axis2],"o", markersize=markersize, markerfacecolor='none',markeredgecolor='blue')
        _plt.plot(cs[axis1],cs[axis2],"o", markersize=markersize, markerfacecolor='none', markeredgecolor='blue')

        _plt.plot(ae[axis1],ae[axis2],"o", markersize=markersize,  markerfacecolor='red', markeredgecolor='red')
        _plt.plot(ce[axis1],ce[axis2],"o", markersize=markersize,  markerfacecolor='red', markeredgecolor='red')

        _plt.plot(am[axis1],am[axis2],"+", markersize=markersize,  markeredgecolor='green')
        _plt.plot(cm[axis1],cm[axis2],"x", markersize=markersize,  markeredgecolor='green')

        if coordinates.element_category[i] == "drift" :
            bp_facecolor = 'black'
            bp_facealpha = 0.5
        elif coordinates.element_category[i] == "rbend" :
            bp_facecolor = 'blue'
            bp_facealpha = 0.5
        elif coordinates.element_category[i] == "sbend" :
            bp_facecolor = 'blue'
            bp_facealpha = 0.5
        elif coordinates.element_category[i] == "quadrupole" :
            bp_facecolor = 'red'
            bp_facealpha = 0.5
        else :
            bp_facecolor = 'green'
            bp_facealpha = 0.5

        if not plotFilledElements :
            bp_facecolor = 'white'

        bounding_poly = _makeBoundingPolygon(bp[:,[axis1,axis2]],
                                             facecolor = bp_facecolor,
                                             facealpha = bp_facealpha)

        _plt.gca().add_patch(bounding_poly)

        if plotNormals :
            fac_sta_arrow = _makeVectorArrow([cs[axis1], cs[axis2]], [fi[axis1],fi[axis2]],500., 0,
                                             color="blue")
            _plt.gca().add_patch(fac_sta_arrow)

            fac_end_arrow = _makeVectorArrow([ce[axis1], ce[axis2]], [fe[axis1],fe[axis2]], 500.0, 0,
                                             color="red")
            _plt.gca().add_patch(fac_end_arrow)

    labels = ["x/mm", "y/mm", "z/mm"]
    _plt.xlabel(labels[axis1])
    _plt.ylabel(labels[axis2])

    return ax

def plot_coordinates_3d(coordinates) :
    ax = _plt.gcf().add_subplot(111, projection='3d')

    orbit = _np.empty((_np.array(coordinates.arc_sta).shape[0]*3,
                      _np.array(coordinates.arc_sta).shape[1]))
    chord = _np.empty((_np.array(coordinates.cho_sta).shape[0]*2,
                      _np.array(coordinates.cho_sta).shape[1]))

    orbit[0::3] = coordinates.arc_sta
    orbit[1::3] = coordinates.arc_mid
    orbit[2::3] = coordinates.arc_end
    orbit = orbit * 1000

    chord[0::2] = coordinates.cho_sta
    chord[1::2] = coordinates.cho_end
    chord = chord * 1000

    for i in range(0, len(coordinates), 1):
        ax.plot(orbit[:,0], orbit[:,1], orbit[:,2], color='black')
        ax.plot(chord[:,0], chord[:,1], chord[:,2], color='black', linestyle='--')


        ax.scatter(_np.array(coordinates.cho_sta)[:,0] * 1000,
                   _np.array(coordinates.cho_sta)[:,1] * 1000,
                   _np.array(coordinates.cho_sta)[:,2] * 1000,
                   facecolors='red', edgecolors='red', marker='o', s=50)

        ax.scatter(_np.array(coordinates.cho_mid)[:,0] * 1000,
                   _np.array(coordinates.cho_mid)[:,1] * 1000,
                   _np.array(coordinates.cho_mid)[:,2] * 1000,
                   c='green', marker="+", s=50)

        ax.scatter(_np.array(coordinates.arc_mid)[:,0] * 1000,
                   _np.array(coordinates.arc_mid)[:,1] * 1000,
                   _np.array(coordinates.arc_mid)[:,2] * 1000,
                   c='green', marker="x", s=50)

        ax.scatter(_np.array(coordinates.cho_end)[:,0] * 1000,
                   _np.array(coordinates.cho_end)[:,1] * 1000,
                   _np.array(coordinates.cho_end)[:,2] * 1000,
                   facecolors='blue', edgecolors='blue', marker='o', s=60)

        ax.quiver(*(coordinates.cho_sta[i]*1000), *(coordinates.fac_sta[i] * 1000/3), color='red')
        ax.quiver(*(coordinates.cho_end[i]*1000), *(coordinates.fac_end[i] * 1000/3), color='blue')

    ax.set_xlabel("x/mm")
    ax.set_ylabel("y/mm")
    ax.set_zlabel("z/mm")

def plot_coordinates_trapezoid(coords) :
    _plt.plot(coords[:,0], coords[:,1])
    _plt.xlabel("x/m")
    _plt.ylabel("y/m")

def plot_bookkeeping(bookkeeping) :
    elements = bookkeeping['elements']

    switch_marker = True
    for k in elements :
        element = elements[k]
        centre = _np.array(element['geomtranslation'])
        rotation = _np.array(element['rotation'])
        length = element['length']
        if element['category'] == "sbend" :
            theta = element['angle']
            length_half = _np.array([0, 0, length * 1000]) * 2 * _np.sin(theta / 2) / theta / 2
            start = centre - rotation @ length_half
            end   = centre + rotation @ length_half
        else :
            length_half = _np.array([0, 0, length * 1000]) / 2
            start = centre - rotation @ length_half
            end   = centre + rotation @ length_half

        if switch_marker :
            _plt.plot([start[2], end[2]], [start[0], end[0]], "+--")
            switch_marker = False
        else :
            _plt.plot([start[2], end[2]], [start[0], end[0]], "o--")
            switch_marker = True

def _makeBoundingRect(centre, size, angle,
                      fill=False,
                      edgecolor="black",
                      linestyle="-",
                      linewidth = 1) :
    cen = _np.array(centre)
    size  = _np.array(size)
    rr = _np.array([[_np.cos(angle), -_np.sin(angle)],
                    [_np.sin(angle),  _np.cos(angle)]])
    ll = cen - rr @ size/2

    return  _patches.Rectangle(ll, size[0], size[1],
                               angle=angle / _np.pi * 180,
                               fill=False,
                               edgecolor=edgecolor,
                               linestyle=linestyle)

def _makeBoundingTrap(centre, size, angle, e1 = 0 , e2 = 0,
                      fill=True,
                      facecolor = 'blue',
                      facealpha = 0.25,
                      edgecolor = 'black',
                      linestyle = "-",
                      linewidth = 1) :

    cen = _np.array(centre)
    size  = _np.array(size)
    rr = _np.array([[_np.cos(angle), -_np.sin(angle)],
                    [_np.sin(angle),  _np.cos(angle)]])
    ll = cen - rr @ size/2

    points = _np.array([[-size[0]/2 + size[1]/2 * _np.tan(e1), -size[1]/2],
                        [-size[0]/2 - size[1]/2 * _np.tan(e1),  size[1]/2],
                        [ size[0]/2 + size[1]/2 * _np.tan(e2),  size[1]/2],
                        [ size[0]/2 - size[1]/2 * _np.tan(e2), -size[1]/2]])

    points = (rr @ points.T).T + cen

    trapezoid = _patches.Polygon(points, closed=True,
                                 fill=True,
                                 facecolor=facecolor,
                                 alpha=facealpha,
                                 edgecolor=edgecolor,
                                 linestyle=linestyle,
                                 linewidth=linewidth)

    return trapezoid

def _makeBoundingPolygon(points,
                         fill=True,
                         facecolor='blue',
                         facealpha=0.25,
                         edgecolor='black',
                         linestyle="-",
                         linewidth=1) :
    points = _sort_clockwise(points)
    polygon = _patches.Polygon(points, closed=True,
                               fill=True,
                               facecolor=facecolor,
                               alpha=facealpha,
                               edgecolor=edgecolor,
                               linestyle=linestyle,
                               linewidth=linewidth)
    return polygon

def _makeVectorArrow(base, dir, length, angle,
                     color="blue") :
    rr = _np.array([[_np.cos(angle), -_np.sin(angle)],
                    [_np.sin(angle),  _np.cos(angle)]])

    return _patches.FancyArrowPatch(base, base + rr @ _np.array(dir) * length,
                                    arrowstyle="-|>", mutation_scale=20,
                                    color=color, lw=1)

