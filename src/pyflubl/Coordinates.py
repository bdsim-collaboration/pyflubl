import numpy as _np
import json as _json

from .Element import Element as _Element
from .Line import Line as _Line

def _CalculateBoundingCuboidOriginCentred( width = 0.1, height = 0.1, length = 1.0):
    # calculate the corners of the bounding cuboid

    arb_r1 = _np.array([-length/2, -width/2, -height/2])
    arb_r2 = _np.array([-length/2,  width/2, -height/2])
    arb_r3 = _np.array([ length/2,  width/2, -height/2])
    arb_r4 = _np.array([ length/2, -width/2, -height/2])

    arb_r5 = _np.array([-length/2, -width/2,  height/2])
    arb_r6 = _np.array([-length/2,  width/2,  height/2])
    arb_r7 = _np.array([ length/2,  width/2,  height/2])
    arb_r8 = _np.array([ length/2, -width/2,  height/2])

    return _np.array([arb_r1, arb_r2, arb_r3, arb_r4, arb_r5, arb_r6, arb_r7, arb_r8])

def _CalculateBoundingTrapezoidOriginCentred(width = 0.1, height = 0.1, length = 1.0,
                                             e1 = 0.0, e2 = 0.0) :
    # origin centred trapezoidal prism with parallel edges parallel to x, units in mm
    # pole face rotation around z, units in mm

    arb_r1 = _np.array([-length/2 - width/2*_np.tan(e1), -width/2, -height/2])
    arb_r2 = _np.array([-length/2 + width/2*_np.tan(e1),  width/2, -height/2])
    arb_r3 = _np.array([ length/2 - width/2*_np.tan(e2),  width/2, -height/2])
    arb_r4 = _np.array([ length/2 + width/2*_np.tan(e2), -width/2, -height/2])

    arb_r5 = _np.array([-length/2 - width/2*_np.tan(e1), -width/2,  height/2])
    arb_r6 = _np.array([-length/2 + width/2*_np.tan(e1),  width/2,  height/2])
    arb_r7 = _np.array([ length/2 - width/2*_np.tan(e2),  width/2,  height/2])
    arb_r8 = _np.array([ length/2 + width/2*_np.tan(e2), -width/2,  height/2])

    return _np.array([arb_r1, arb_r2, arb_r3, arb_r4, arb_r5, arb_r6, arb_r7, arb_r8])

def _CalculateBoundingTrapezoidOriginCentredNew(width = 0.1, height = 0.1, length = 1.0,
                                                e1 = 0.0, e2 = 0.0,
                                                p1 = 0.0, p2 = 0.0) :
    # origin centred trapezoidal prism with parallel edges parallel to x, units in mm
    # pole face rotation around z, units in mm

    # not normal polar resolution as z -> x, x -> y, y -> z
    n1 = _np.array([-_np.cos(e1), _np.sin(e1)*_np.cos(p1), _np.sin(e1)*_np.sin(p1)])
    n2 = _np.array([ _np.cos(e2), _np.sin(e2)*_np.cos(p2), _np.sin(e2)*_np.sin(p2)])

    d1 = _np.dot(n1,_np.array([-length/2,0,0]))
    d2 = _np.dot(n2,_np.array([ length/2,0,0]))

    # nx*x + ny*y + nz*z = d, need x in terms of y and z to calculate the corners of the trapezoid
    # x = (d - ny*y - nz*z)/nx

    def x(n, d, y, z) :
        return (d - n[1]*y - n[2]*z)/n[0]

    arb_r1 = _np.array([ x(n1, d1, -width/2, -height/2), -width/2, -height/2])
    arb_r2 = _np.array([ x(n1, d1,  width/2, -height/2),  width/2, -height/2])
    arb_r3 = _np.array([ x(n2, d2,  width/2, -height/2),  width/2, -height/2])
    arb_r4 = _np.array([ x(n2, d2, -width/2, -height/2), -width/2, -height/2])

    arb_r5 = _np.array([ x(n1, d1, -width/2,  height/2), -width/2,  height/2])
    arb_r6 = _np.array([ x(n1, d1,  width/2,  height/2),  width/2,  height/2])
    arb_r7 = _np.array([ x(n2, d2,  width/2,  height/2),  width/2,  height/2])
    arb_r8 = _np.array([ x(n2, d2, -width/2,  height/2), -width/2,  height/2])

    return _np.array([arb_r1, arb_r2, arb_r3, arb_r4, arb_r5, arb_r6, arb_r7, arb_r8])

def _RotateFromXTrapToZTrap(pnts) :

    rot_z = _np.array([[ _np.cos(-_np.pi/2), -_np.sin(-_np.pi/2), 0],
                       [ _np.sin(-_np.pi/2),  _np.cos(-_np.pi/2), 0],
                       [                  0,                   0, 1]])

    rot_x = _np.array([[1,                 0,                     0],
                       [0,  _np.cos(-_np.pi/2), -_np.sin(-_np.pi/2)],
                       [0,  _np.sin(-_np.pi/2) , _np.cos(-_np.pi/2)]])

    return (rot_x @ rot_z @ pnts.T).T

def _CalculateElementTransformation(e):

    # if an instance of a lattice prototype. Replace element
    # with that looked up from Builder.prototypes
    if e.category == "lattice_instance" :
        e = e['prototype']

    if e.category in ["drift", "quadrupole", "target", "rcol", "ecol", "jcol",
                      "shield", "dump", "wirescanner", "gap", "customG4", "customFluka",
                      "sampler_plane"] :

        l = e.length
        c = l
        outerE1 = e['outerE1']
        outerE2 = e['outerE2']
        outerP1 = e['outerP1']
        outerP2 = e['outerP2']

        rotation = _np.array([[1,0,0],
                              [0,1,0],
                              [0,0,1]])

        rot_sta = rotation
        rot_mid = rotation
        rot_end = rotation

        arc_sta = _np.array([0,0,0])
        arc_end = _np.array([0,0,l])
        arc_mid = arc_end/2.

        cho_sta = arc_sta
        cho_mid = arc_mid
        cho_end = arc_end

        s_sta = 0
        s_mid = l/2.0
        s_end = l

        fac_sta = _np.array([_np.sin(outerE1)*_np.cos(outerP1), _np.sin(outerE1)*_np.sin(outerP1), -_np.cos(outerE1)])
        fac_end = _np.array([_np.sin(outerE2)*_np.cos(outerP2), _np.sin(outerE2)*_np.sin(outerP2),  _np.cos(outerE2)])

        fac_sta = rot_mid @ fac_sta
        fac_end = rot_mid @ fac_end

        outerHorizontalSize = e['outerHorizontalSize'] / 1000
        outerVerticalSize = e['outerVerticalSize'] / 1000

        if e.category == "sampler_plane" :
            outerHorizontalSize = e['samplerDiameter'] / 1000
            outerVerticalSize = e['samplerDiameter'] / 1000

        # local cubical bounding box
        cub_loc = _CalculateBoundingCuboidOriginCentred(width  = outerHorizontalSize,
                                                        height = outerVerticalSize,
                                                        length = l)
        # local trapezoidal prism bounding box (+x aligned)
        tra_loc = _CalculateBoundingTrapezoidOriginCentredNew(width  = outerHorizontalSize,
                                                              height = outerVerticalSize,
                                                              length = l,
                                                              e1=outerE1,
                                                              e2=outerE2,
                                                              p1=outerP1,
                                                              p2=outerP2)

        # transform local cubical bounding box to global coordinates
        cub = (rot_mid @ _RotateFromXTrapToZTrap(cub_loc).T).T + cho_mid;

        # transform local trapezoidal prism to global coordinates (need to rotate from +x to +z aligned first)
        tra = (rot_mid @ _RotateFromXTrapToZTrap(tra_loc).T).T + cho_mid;

        return {"rot_sta":rot_sta, "rot_mid":rot_mid, "rot_end":rot_end,
                "arc_sta":arc_sta, "arc_mid":arc_mid, "arc_end":arc_end,
                "cho_sta":cho_sta, "cho_mid":cho_mid, "cho_end":cho_end,
                "s_sta":s_sta,     "s_mid":s_mid,     "s_end":s_end,
                "fac_sta":fac_sta                   , "fac_end":fac_end,
                "cub_loc":cub_loc, "tra_loc":tra_loc,
                "cub":cub,         "tra":tra}

    elif e.category == "rbend":
        # length is chord length

        a = e['angle']
        l = e.length
        c = l
        t = 0
        if 'tilt' in e :
            t = e['tilt']

        if abs(a) < 1e-12:
            print("rbend: angle close to zero setting to 1e-12")
            a = 1e-12

        # outer face rotations
        outerE1 = e['outerE1']
        outerE2 = e['outerE2']

        # bending radius
        rho = l/(2*_np.sin(a/2.0))

        tilt = _np.array([[ _np.cos(t), -_np.sin(t), 0],
                          [ _np.sin(t),  _np.cos(t), 0],
                          [ 0         ,           0, 1]])

        rot_sta = _np.array([[1, 0, 0],
                             [0, 1, 0],
                             [0, 0, 1]])
        rot_mid = _np.array([[ _np.cos(a/2), 0, -_np.sin(a/2)],
                             [            0, 1,             0],
                             [ _np.sin(a/2), 0, _np.cos(a/2)]])
        rot_end = _np.array([[ _np.cos(a), 0, -_np.sin(a)],
                             [          0, 1,           0],
                             [ _np.sin(a), 0,  _np.cos(a)]])


        rot_sta = tilt @ rot_sta @ _np.linalg.inv(tilt)
        rot_mid = tilt @ rot_mid @ _np.linalg.inv(tilt)
        rot_end = tilt @ rot_end @ _np.linalg.inv(tilt)

        arc_sta = _np.array([0,0,0])
        arc_mid = _np.array([rho*(_np.cos(a/2.) - 1),0,rho*_np.sin(a/2.)])
        arc_end = _np.array([rho*(_np.cos(a) - 1),0,rho*_np.sin(a)])

        cho_sta = _np.array([0,0,0])
        cho_end = l * _np.array([-_np.sin(a/2),0,_np.cos(a/2)])
        cho_mid = cho_end/2.0

        arc_sta = tilt @ arc_sta
        arc_mid = tilt @ arc_mid
        arc_end = tilt @ arc_end

        cho_sta = tilt @ cho_sta
        cho_mid = tilt @ cho_mid
        cho_end = tilt @ cho_end

        s_sta = 0
        s_mid = l/2
        s_end = l

        fac_sta = _np.array([_np.sin(outerE1), 0, -_np.cos(outerE1)])
        fac_end = _np.array([_np.sin(outerE2), 0,  _np.cos(outerE2)])

        fac_sta = rot_mid @ tilt @ fac_sta
        fac_end = rot_mid @ tilt @ fac_end

        # local cubical bounding box
        cub_loc = _CalculateBoundingCuboidOriginCentred(width=e['outerHorizontalSize'] / 1000,
                                                        height=e['outerVerticalSize'] / 1000,
                                                        length=l)
        # local trapezoidal prism bounding box (+x aligned)
        tra_loc = _CalculateBoundingTrapezoidOriginCentred(width=e['outerHorizontalSize'] / 1000,
                                                           height=e['outerVerticalSize'] / 1000,
                                                           length=l,
                                                           e1=outerE1,
                                                           e2=outerE2)

        # transform local cubical bounding box to global coordinates
        cub = (rot_mid @ tilt @ _RotateFromXTrapToZTrap(cub_loc).T).T + cho_mid;

        # transform local trapezoidal prism to global coordinates (need to rotate from +x to +z aligned first)
        tra = (rot_mid @ tilt @ _RotateFromXTrapToZTrap(tra_loc).T).T + cho_mid;

        return {"rot_sta":rot_sta, "rot_mid":rot_mid, "rot_end":rot_end,
                "arc_sta":arc_sta, "arc_mid":arc_mid, "arc_end":arc_end,
                "cho_sta":cho_sta, "cho_mid":cho_mid, "cho_end":cho_end,
                "s_sta": s_sta,    "s_mid": s_mid,    "s_end": s_end,
                "fac_sta":fac_sta                   , "fac_end":fac_end,
                "cub_loc":cub_loc, "tra_loc":tra_loc,
                "cub":cub,         "tra":tra}


    elif e.category == "sbend":
        # length is arc length

        a = e['angle']
        l = e.length
        c = 2*(l/a)*_np.sin(a/2)
        t = 0
        if 'tilt' in e:
            t = e['tilt']

        if abs(a) < 1e-12:
            print("sbend: angle close to zero setting to 1e-12")
            a = 1e-12

        # outer face rotations
        outerE1 = e['outerE1']
        outerE2 = e['outerE2']

        # bending radius
        rho = l/a

        tilt = _np.array([[ _np.cos(t), -_np.sin(t), 0],
                          [ _np.sin(t),  _np.cos(t), 0],
                          [          0,           0, 1]])

        rot_sta = _np.array([[1, 0, 0],
                             [0, 1, 0],
                             [0, 0, 1]])
        rot_mid = _np.array([[ _np.cos(a/2), 0, -_np.sin(a/2)],
                             [          0, 1,          0],
                             [_np.sin(a/2), 0, _np.cos(a/2)]])
        rot_end = _np.array([[ _np.cos(a), 0, -_np.sin(a)],
                             [          0, 1,          0],
                             [_np.sin(a), 0, _np.cos(a)]])

        rot_sta = tilt @ rot_sta @ _np.linalg.inv(tilt)
        rot_mid = tilt @ rot_mid @ _np.linalg.inv(tilt)
        rot_end = tilt @ rot_end @ _np.linalg.inv(tilt)

        arc_sta = _np.array([0,0,0])
        arc_mid = _np.array([rho*(_np.cos(a/2) - 1),0,rho*_np.sin(a/2)])
        arc_end = _np.array([rho*(_np.cos(a) - 1),0,rho*_np.sin(a)])

        cho_sta = _np.array([0,0,0])
        cho_end = c * _np.array([-_np.sin(a/2),0,_np.cos(a/2)])
        cho_mid = cho_end/2.0

        arc_sta = tilt @ arc_sta
        arc_mid = tilt @ arc_mid
        arc_end = tilt @ arc_end

        cho_sta = tilt @ cho_sta
        cho_mid = tilt @ cho_mid
        cho_end = tilt @ cho_end

        s_sta = 0
        s_mid = c/2
        s_end = c

        fac_sta = _np.array([_np.sin(outerE1),0, -_np.cos(outerE1)])
        fac_end = _np.array([_np.sin(outerE2),0, _np.cos(outerE2)])

        fac_sta = rot_mid @ tilt @ fac_sta
        fac_end = rot_mid @ tilt @ fac_end

        # local cubical bounding box ((+x aligned)
        cub_loc = _CalculateBoundingCuboidOriginCentred(width=e['outerHorizontalSize'] / 1000,
                                                        height=e['outerVerticalSize'] / 1000,
                                                        length=c)
        # local trapezoidal prism bounding box (+x aligned)
        tra_loc = _CalculateBoundingTrapezoidOriginCentred(width=e['outerHorizontalSize'] / 1000,
                                                           height=e['outerVerticalSize'] / 1000,
                                                           length=c,
                                                           e1=outerE1,
                                                           e2=outerE2)

        # transform local cubical bounding box to global coordinates
        cub = (rot_mid @ tilt @ _RotateFromXTrapToZTrap(cub_loc).T).T + cho_mid;

        # transform local trapezoidal prism to global coordinates (need to rotate from +x to +z aligned first)
        tra = (rot_mid @ tilt @ _RotateFromXTrapToZTrap(tra_loc).T).T + cho_mid;

        return {"rot_sta":rot_sta, "rot_mid":rot_mid, "rot_end":rot_end,
                "arc_sta":arc_sta, "arc_mid":arc_mid, "arc_end":arc_end,
                "cho_sta":cho_sta, "cho_mid":cho_mid, "cho_end":cho_end,
                "s_sta": s_sta,    "s_mid": s_mid,    "s_end": s_end,
                "fac_sta":fac_sta                   , "fac_end":fac_end,
                "cub_loc":cub_loc, "tra_loc":tra_loc,
                "cub":tra,         "tra":tra}

class Coordinates(object) :

    def __init__(self):
        # units in m

        self.sequence = []
        self.elements = {}

        self.element_name = [] # name of element
        self.element_category = [] # type of element
        self.element_length = [] # length of element
        self.element_theta = [] # rotation around y
        self.element_psi   = [] # rotation around z
        self.element_chord_length = [] # length of element along chord

        self.Clear()

        self.ibuild = 0

    def Clear(self):
        self.element_name = []
        self.element_category = []
        self.element_length = []
        self.element_theta = []
        self.element_psi = []
        self.element_chord_length = []

        self.len_sta = [] # length along reference trajectory at start of element
        self.len_mid = [] # length along reference trajectory at middle of element
        self.len_end = [] # length along reference trajectory at end of element

        self.rot_sta = [] # rotation of reference trajectory at start
        self.rot_mid = [] # rotation of reference trajectory at middle
        self.rot_end = [] # rotation of reference trajectory at end

        self.arc_sta = [] # arc position at start
        self.arc_mid = [] # arc position at middle
        self.arc_end = [] # arc position at end

        self.cho_sta = [] # chord position at start
        self.cho_mid = [] # chord position at middle
        self.cho_end = [] # chord position at end

        self.s_sta = [] # curvilinear position at start
        self.s_mid = [] # curvilinear position at middle
        self.s_end = [] # curvilinear position at end

        self.fac_sta = [] # normal vector to face at start of element
        self.fac_end = [] # normal vector to face at end of element

        # cub/tra 6 face wed/raw/arb (first 4 loop clockwise around -z axis,
        # second 4 loop clockwise around +z axis)
        self.cub_loc = [] # cubical local
        self.tra_loc = [] # trapezoidal prism local

        self.cub = [] # cubical global
        self.tra = [] # trapezoidal prism global

    def Append(self, item, addToSequence=True):
        if not isinstance(item, (_Element, _Line)):
            msg = "Only Elements or Lines can be added to the machine"
            raise TypeError(msg)
        elif item.name not in list(self.elements.keys()):
            #hasn't been used before - define it
            if type(item) is _Line:
                for element in item:
                    self.Append(item)
            else:
                self.elements[item.name] = item
        else:
            raise ValueError(f"Coordinate.Append({item.name})  already in machine")

        # add to the sequence - optional as we may be appending a parent definition to the list
        # of objects to write before the main definitions.
        if addToSequence:
            self.sequence.append(item.name)

    def __len__(self):
        return max(len(self.elements), len(self.element_name))

    def Build(self, circular = False):

        self.Clear()

        for element_name in self.elements :
            e = self.elements[element_name]
            t = _CalculateElementTransformation(e)

            # name
            self.element_name.append(e.name)

            # length
            self.element_length.append(e.length)

            # category
            self.element_category.append(e.category)

            # bending angle
            try :
                self.element_theta.append(e['angle'])
                if e.category == "rbend" :
                    self.element_chord_length.append(e.length)
                elif e.category == "sbend" :
                    chord = 2 * (e.length / e['angle']) * _np.sin(e['angle'] / 2)
                    self.element_chord_length.append(chord)
            except KeyError :
                self.element_theta.append(0)
                self.element_chord_length.append(e.length)

            # tilt angle
            try :
                self.element_psi.append(e['tilt'])
            except KeyError :
                self.element_psi.append(0)

            if len(self.rot_sta) == 0:
                self.len_sta.append(0)
                self.len_mid.append(e.length/2.0)
                self.len_end.append(e.length)
                self.rot_sta.append(t['rot_sta'])
                self.rot_mid.append(t['rot_mid'])
                self.rot_end.append(t['rot_end'])
                self.arc_sta.append(t['arc_sta'])
                self.arc_mid.append(t['arc_mid'])
                self.arc_end.append(t['arc_end'])
                self.cho_sta.append(t['cho_sta'])
                self.cho_mid.append(t['cho_mid'])
                self.cho_end.append(t['cho_end'])
                self.s_sta.append(t['s_sta'])
                self.s_mid.append(t['s_mid'])
                self.s_end.append(t['s_end'])
                self.fac_sta.append(t['fac_sta'])
                self.fac_end.append(t['fac_end'])

                # append bounding boxes (both local and global coordinates)
                self.cub_loc.append(t['cub_loc'])
                self.tra_loc.append(t['tra_loc'])

                self.cub.append(t['cub'])
                self.tra.append(t['tra'])
            else:
                # get last element variables
                len_end = self.len_end[-1]
                rot_end = self.rot_end[-1]
                arc_end = self.arc_end[-1]
                s_end   = self.s_end[-1]

                self.len_sta.append(len_end + 0)
                self.len_mid.append(len_end + e.length/2.0)
                self.len_end.append(len_end + e.length)

                self.rot_sta.append(rot_end @ t['rot_sta'] )
                self.rot_mid.append(rot_end @ t['rot_mid'] )
                self.rot_end.append(rot_end @ t['rot_end'] )

                self.arc_sta.append(rot_end @ t['arc_sta'] + arc_end)
                self.arc_mid.append(rot_end @ t['arc_mid'] + arc_end)
                self.arc_end.append(rot_end @ t['arc_end'] + arc_end)
                self.cho_sta.append(rot_end @ t['cho_sta'] + arc_end)
                self.cho_mid.append(rot_end @ t['cho_mid'] + arc_end)
                self.cho_end.append(rot_end @ t['cho_end'] + arc_end)
                self.s_sta.append(s_end + t['s_sta'])
                self.s_mid.append(s_end + t['s_mid'])
                self.s_end.append(s_end + t['s_end'])

                self.fac_sta.append(rot_end @ t['fac_sta'])
                self.fac_end.append(rot_end @ t['fac_end'])

                # append bounding boxes (both local and global coordinates)
                self.cub_loc.append(t['cub_loc'])
                self.tra_loc.append(t['tra_loc'])

                self.cub.append((rot_end @ t['cub'].T).T + arc_end)
                self.tra.append((rot_end @ t['tra'].T).T + arc_end)

        # keep a build counter to terminate infinite recursion
        self.ibuild += 1

        # check pole faces before bounding cube/trapezoid
        #if self._CheckPoleFaces() and self.ibuild < 2 :
        if self._CheckPoleFaces() :
            self.Clear()
            self.Build(circular)


    def CalculateExtent(self):
        # TODO improve with extent of traps

        # loop over positions and find maxima
        vmin = [9e99, 9e99, 9e99]
        vmax = [-9e99, -9e99, -9e99]

        for p_start, p_end in zip(self.cho_sta,self.cho_end) :

            xmin = min(p_start[0], p_end[0])
            ymin = min(p_start[1], p_end[1])
            zmin = min(p_start[2], p_end[2])

            xmax = max(p_start[0], p_end[0])
            ymax = max(p_start[1], p_end[1])
            zmax = max(p_start[2], p_end[2])

            if xmin < vmin[0] :
                vmin[0] = xmin
            if ymin < vmin[1] :
                vmin[1] = ymin
            if zmin < vmin[2] :
                vmin[2] = zmin

            if xmax > vmax[0]:
                vmax[0] = xmax
            if ymax > vmax[1] :
                vmax[1] = ymax
            if zmax > vmax[2] :
                vmax[2] = zmax

        vmin = [x-2 for x in vmin]
        vmax = [x+2 for x in vmax]

        return [vmin,vmax]

    def _CheckPoleFaces(self, circular = False):
        update = False

        for i, element_name in enumerate(self.elements) :

            # current and next element indices
            i1 = i
            if i < len(self.elements)-1 :
                i2 = i+1
            else :
                if circular :
                    i2 = 0
                else :
                    continue

            i1name = list(self.elements.keys())[i1]
            i2name = list(self.elements.keys())[i2]

            if _np.abs(self.fac_end[i1] + self.fac_sta[i2]).sum() > 1e-8:
                if self.element_category[i1] == "drift" and self.element_category[i2] == "rbend":
                    self.elements[i1name]['outerE2'] = -self.elements[i2name]['angle']/2.0
                    self.elements[i1name]['outerP2'] = self.elements[i2name]['tilt']
                    update = True

                if self.element_category[i1] == "rbend" and self.element_category[i2] == "drift":
                    self.elements[i2name]['outerE1'] = -self.elements[i1name]['angle']/2.0
                    self.elements[i2name]['outerP1'] = self.elements[i1name]['tilt']
                    update = True

        return update

    def SaveJSON(self, file_name, indent = 0):

        self.Build()

        dict_to_save = {}

        dict_to_save['element_name'] = self.element_name
        dict_to_save['element_category'] = self.element_category
        dict_to_save['element_length'] = self.element_length
        dict_to_save['element_theta'] = self.element_theta
        dict_to_save['element_psi'] = self.element_psi
        dict_to_save['element_chord_length'] = self.element_chord_length

        dict_to_save['len_sta'] = self.len_sta
        dict_to_save['len_mid'] = self.len_mid
        dict_to_save['len_end'] = self.len_end

        dict_to_save['rot_sta'] = _np.array(self.rot_sta).tolist()
        dict_to_save['rot_mid'] = _np.array(self.rot_mid).tolist()
        dict_to_save['rot_end'] = _np.array(self.rot_end).tolist()

        dict_to_save['arc_sta'] = _np.array(self.arc_sta).tolist()
        dict_to_save['arc_mid'] = _np.array(self.arc_mid).tolist()
        dict_to_save['arc_end'] = _np.array(self.arc_end).tolist()

        dict_to_save['cho_sta'] = _np.array(self.cho_sta).tolist()
        dict_to_save['cho_mid'] = _np.array(self.cho_mid).tolist()
        dict_to_save['cho_end'] = _np.array(self.cho_end).tolist()

        dict_to_save['fac_sta'] = _np.array(self.fac_sta).tolist()
        dict_to_save['fac_end'] = _np.array(self.fac_end).tolist()

        dict_to_save['cub_loc'] = _np.array(self.cub_loc).tolist()
        dict_to_save['tra_loc'] = _np.array(self.tra_loc).tolist()

        dict_to_save['cub'] = _np.array(self.cub).tolist()
        dict_to_save['tra'] = _np.array(self.tra).tolist()

        # Pretty-printed
        with open(file_name, "w") as f:
            if indent > 0 :
                _json.dump(dict_to_save, f, indent=indent)
            else :
                _json.dump(dict_to_save, f)

    def LoadJSON(self, file_name):
        with open(file_name, "r") as f:
            data = _json.load(f)

            self.element_name = data['element_name']
            self.element_category = data['element_category']
            self.element_length = data['element_length']
            self.element_theta = data['element_theta']
            self.element_psi = data['element_psi']
            self.element_chord_length = data['element_chord_length']

            self.len_sta = data['len_sta']
            self.len_mid = data['len_mid']
            self.len_end = data['len_end']

            # make list elements arrays
            self.rot_sta = [_np.array(e) for e in data['rot_sta']]
            self.rot_mid = [_np.array(e) for e in data['rot_mid']]
            self.rot_end = [_np.array(e) for e in data['rot_end']]

            self.arc_sta = [_np.array(e) for e in data['arc_sta']]
            self.arc_mid = [_np.array(e) for e in data['arc_mid']]
            self.arc_end = [_np.array(e) for e in data['arc_end']]

            self.cho_sta = [_np.array(e) for e in data['cho_sta']]
            self.cho_mid = [_np.array(e) for e in data['cho_mid']]
            self.cho_end = [_np.array(e) for e in data['cho_end']]

            self.fac_sta = [_np.array(e) for e in data['fac_sta']]
            self.fac_end = [_np.array(e) for e in data['fac_end']]

            self.cub_loc = [_np.array(e) for e in data['cub_loc']]
            self.tra_loc = [_np.array(e) for e in data['tra_loc']]

            self.cub = [_np.array(e) for e in data['cub']]
            self.tra = [_np.array(e) for e in data['tra']]



    def PandasDataFrame(self):
        import pandas as pd
        df = pd.DataFrame()
        df['element_name'] = self.element_name
        df['element_category'] = self.element_category
        df['element_length'] = self.element_length
        df['element_theta'] = self.element_theta
        df['element_psi'] = self.element_psi

        df['len_sta'] = self.len_sta
        df['len_mid'] = self.len_mid
        df['len_end'] = self.len_end

        df['rot_sta'] = self.rot_sta
        df['rot_mid'] = self.rot_mid
        df['rot_end'] = self.rot_end

        df['arc_sta'] = self.arc_sta
        df['arc_mid'] = self.arc_mid
        df['arc_end'] = self.arc_end

        df['cho_sta'] = self.cho_sta
        df['cho_mid'] = self.cho_mid
        df['cho_end'] = self.cho_end

        df['fac_sta'] = self.fac_sta
        df['fac_end'] = self.fac_end

        df['cub_loc'] = self.cub_loc
        df['tra_loc'] = self.tra_loc

        df['cub'] = self.cub
        df['tra'] = self.tra

        return df