try: # Deprecated, removed in Python 3.10
    from collections import MutableMapping as _MutableMapping
except ImportError: # Python 3.10 onwards.
    from collections.abc import MutableMapping as _MutableMapping
import numbers as _numbers

import numpy as _np

class ElementBase(_MutableMapping):
    """
    A class that represents an element / item in an accelerator beamline.
    Printing or string conversion produces the BDSIM syntax.

    This class provides the basic dict(ionary) inheritance and functionality
    and the representation that allows modification of existing parameters
    of an already declared item.

    """
    def __init__(self, name, isMultipole=False, **kwargs):
        self._store = dict()
        self.name         = name
        self['name']      = name
        self._isMultipole = isMultipole
        self._keysextra   = set()
        for k, v in kwargs.items():
            self[k] = v

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        if (key == "name" or key == "category") and value:
            self._store[key] = value
        elif value == "":
            return
        elif type(value) == tuple and self._isMultipole:
            self._store[key] = value
        elif isinstance(value, tuple):
            self._store[key] = (float(value[0]), value[1])
        elif isinstance(value, _numbers.Number):
            if "aper" in key.lower() and value < 1e-6:
                return
            else:
                self._store[key] = value
        elif isinstance(value, str):
            if value.startswith('"') and value.endswith('"'):
                # Prevent the buildup of quotes for multiple setitem calls
                value = value.strip('"')
            #self._store[key] = '"{}"'.format(value)
            self._store[key]  = value
        else :
            self._store[key] = value

        if key not in {"name", "category"}: # keys which are not # 'extra'.
            self._keysextra.add(key)

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        return iter(self._store)

    def keysextra(self):
        #so behaviour is similar to dict.keys()
        return self._keysextra

    def __delitem__(self, key):
        del self._store[key]
        try: # it may be in _store, but not necessarily in _keyextra
            self._keysextra.remove(key)
        except:
            pass

    def __repr__(self):
        s = "{s.name}: ".format(s=self)
        for i,key in enumerate(self._keysextra):
            if i > 0: # Separate with commas
                s += ", "
            # Write multipole syntax
            if type(self[key]) == tuple and self._isMultipole:
                s += key + '=' + '{'+(','.join([str(s) for s in self[key]]))+'}'
            # Write tuple (i.e. number + units) syntax
            elif type(self[key]) == tuple:
                s += key + '=' + str(self[key][0]) + '*' + str(self[key][1])
            # everything else (most things!)
            else:
                s += key + '=' + str(self[key])
        s += ';\n'
        return s

class Element(ElementBase):

    _outer_allowed_keys = ["outerHorizontalSize","outerVerticalSize","outerMaterial",
                           "outerE1", "outerE2","outerP1", "outerP2"]
    _beampipe_allowed_keys = ["vacuumMaterial", "beampipeMaterial","beampipeRadius", "beampipeThickness",
                              "e1", "e2"]
    _rbend_allowed_keys = ["angle"]
    _sbend_allowed_keys = ["angle"]
    _tiltshift_allowed_keys = ["offsetX", "offsetY", "tilt"]
    _quadrupole_allowed_keys = ["k1"]
    _sextupole_allowed_keys = ["k2"]
    _octupole_allowed_keys = ["k3"]
    _decapole_allowed_keys = ["k4"]
    _target_allowed_keys = ["material","horizontalWidth","verticalWidth","apertureType"]
    _rcol_allowed_keys = ["xsize", "ysize", "material", "horizontalWidth", "verticalWidth"]
    _ecol_allowed_keys = ["xsize", "ysize", "material", "horizontalWidth", "verticalWidth"]
    _jcol_allowed_keys = ["xsize","ysize","material","xsizeLeft","xsizeRight","jawTiltLeft", "jawTiltRight","horizontalWidth", "verticalWidth"]
    _shield_allowed_keys = ["material","horizontalWidth","verticalWidth",
                            "xsize", "ysize"]
    _dump_allowed_keys = ["horizontalWidth","verticalWidth","apertureType"]
    _wirescanner_allowed_keys = ["wireDiameter","wireLength","wireMaterial","wireAngle",
                                  "wireOffsetX","wireOffsetY","wireOffsetZ"]
    _customg4_allowed_keys = ["customLV","convertMaterials"]
    _customg4file_allowed_keys = ["geometryFile","lvName"]
    _customfluka_allowed_keys = ["customOuterBodies", "customRegions", "flukaRegistry"]
    _customflukafile_allowed_keys = ["geometryFile", "customOuterRegion", "customOuterBodies", "customRegions"]
    _sampler_plane_allowed_keys = ["samplerDiameter", "samplerMaterial", "samplerLength"]

    def __init__(self, name = "element", category = None, length = 0.0,
                 transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]),
                 geometry = None,
                 **kwargs) :

        ElementBase.__init__(self, name, **kwargs)

        if type(name) is not str :
            raise ValueError("Need a str as name")
        if type(category) is not str :
            raise ValueError("Need a str as category")
            if category not in pyflublcategories:
                raise ValueError("Not a valid PYFLUBL element type: {}".format(category))
        if type(transform) is not _np.ndarray :
            raise ValueError("Transform needs to be 3x3 or 1x3 or _np.array")
        if geometry :
            if type(geometry) is not str or type(geometry) is not _pyg4.fluka.FlukaRegistry :
                raise ValueError("Geometry needs to a pyg4ometry fluka registry or fluka input file name")

        self.name = name
        self.category = category
        self.length = length
        self.transform = transform
        self.geometry = geometry

        # copy over kwargs
        for k, v in kwargs.items():
            self[k] = v

    def __repr__(self):
        s = "{}: {}".format(self.name, self.category)
        return s

class SplitOrJoinElement(Element) :
    def __init__(self, length = 0, transforms = None, lines = None, type = "split", **kwargs):

        super().__init__()

        if transforms :
            if type(transforms) is list or type(transforms) is _np.array :
                if transforms[0] is _np.array:
                    self.transforms = transforms
                else :
                    print("transform list element has to be numpy array")
            else :
                print("transform has to be list or numpy array")

        if lines :
            if type(lines) is list  :
                if lines[0] is Line:
                    self.line = line
                else :
                    print("transform list element has to be a Line")
            else :
                print("Lines has to be list")

        if type == "join" :
            self.type = type
        elif type == "split" :
            self.type = type
        else :
            self.type = None
            print("type must be split or join")

    def AddMachine(self, transform, machine):
        pass

# TODO not needed
class ElementCustomG4(Element):
    def __init__(self, name, length, containerLV, transform=_np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]),  **kwargs):
        super().__init__(name, "customG4", length, transform, None, **kwargs)
        self.containerLV = containerLV

# TODO not needed
class ElementCustomFluka(Element):
    def __init__(self, name, length, customOuterBodies, customRegions, flukaRegistry,
                 transform=_np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]), **kwargs):
        super().__init__(name, "customFluka", length, transform, None, **kwargs)
        self.outer_bodies = customOuterBodies
        self.regions = customRegions
        self.fluka_registry = flukaRegistry

# TODO not needed
class ElementGap(Element):
    def __init__(self, name, length, transform=_np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]), **kwargs):
        super().__init__(name, "gap", length, transform, None, **kwargs)