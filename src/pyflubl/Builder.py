try: # Deprecated, removed in Python 3.10
    from collections import MutableMapping as _MutableMapping
except ImportError: # Python 3.10 onwards.
    from collections.abc import MutableMapping as _MutableMapping
import numbers as _numbers

import numpy as _np
import json as _json
import copy as _copy
import pprint as _pprint
from collections import defaultdict as _defaultdict
import random as _random

import pyg4ometry as _pyg4
from pyg4ometry.fluka.directive import rotoTranslationFromTra2 as _rotoTranslationFromTra2
from pyg4ometry.convert.geant42Fluka import geant4PhysicalVolume2Fluka as _geant4PhysicalVolume2Fluka
from pyg4ometry.convert.geant42Fluka import geant4Material2Fluka as _geant4Material2Fluka
from pyg4ometry.transformation import matrix2tbxyz as _matrix2tbxyz
from pyg4ometry.transformation import tbxyz2matrix as _tbxyz2matrix
from pyg4ometry.transformation import tbxyz2axisangle as _tbxyz2axisangle

from .Options import Options as _Options

pyflublcategories = [
    'drift',
    'rbend',
    'sbend',
    'quadrupole',
    'sampler_plane'
    ]


def _CalculateElementTransformation(e):
    if e.category == "drift" or  \
            e.category == "quadrupole" or \
            e.category == "target" or \
            e.category == "rcol" or \
            e.category == "ecol" or \
            e.category == "jcol" or \
            e.category == "gap" or \
            e.category == "customG4" or \
            e.category == "customFluka" :
        rotation = _np.array([[1,0,0],
                              [0,1,0],
                              [0,0,1]])
        midrotation = rotation
        endrotation = rotation
        delta = _np.array([0,0,e.length])
        middelta = delta/2
        enddelta = delta
        return [midrotation, endrotation, delta]
    elif e.category == "rbend":
        a = e['angle']
        l = e.length
        midrotation = _np.array([[ _np.cos(a/2), 0, -_np.sin(a/2)],
                                 [          0, 1,          0],
                                 [_np.sin(a/2), 0, _np.cos(a/2)]])
        endrotation = _np.array([[ _np.cos(a), 0, -_np.sin(a)],
                                 [          0, 1,          0],
                                 [_np.sin(a), 0, _np.cos(a)]])
        delta = _np.array([0,0,l])
        return [midrotation, endrotation, delta]
    elif e.category == "sbend":
        a = e['angle']
        l = e.length
        dz = 2*l/a*_np.sin(a/2)
        midrotation = _np.array([[ _np.cos(a/2), 0, -_np.sin(a/2)],
                                 [          0, 1,          0],
                                 [_np.sin(a/2), 0, _np.cos(a/2)]])
        endrotation = _np.array([[ _np.cos(a), 0, -_np.sin(a)],
                                 [          0, 1,          0],
                                 [_np.sin(a), 0, _np.cos(a)]])
        delta = _np.array([0,0,dz])
        return [midrotation, endrotation, delta]
    elif e.category == "sampler_plane":
        rotation = _np.array([[1,0,0],
                              [0,1,0],
                              [0,0,1]])
        midrotation = rotation
        endrotation = rotation
        delta = _np.array([0,0,e.length])

        return [midrotation, endrotation, delta]

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
        else:
            if value.startswith('"') and value.endswith('"'):
                # Prevent the buildup of quotes for multiple setitem calls
                value = value.strip('"')
            #self._store[key] = '"{}"'.format(value)
            self._store[key]  = value
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

class ElementCustomG4(Element):
    def __init__(self, name, length, containerLV, convertMaterials=False, transform=_np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]), **kwargs):
        super().__init__(name, "customG4", length, transform)
        self.containerLV = containerLV
        self.convertMaterials = convertMaterials

class ElementCustomFluka(Element):
    def __init__(self, name, length, customOuterBodies, customRegions, flukaRegistry,
                 transform=_np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]), **kwargs):
        super().__init__(name, "customFluka", length, transform)
        self.outer_bodies = customOuterBodies
        self.regions = customRegions
        self.fluka_registry = flukaRegistry

class ElementGap(Element):
    def __init__(self, name, length, transform=_np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        super().__init__(name, "gap", length, transform)

class Line(list) :
    def __init__(self, name, *args):
        self.category = "line"
        for item in args[0]:
            if type(item) != Element:
                raise TypeError("Line is a list of Elements")

        list.__init__(self,*args)
        self.name   = name
        self.length = 0.0
        for item in args[0]:
            self.length += item.length

    def __repr__(self):
        s = ''
        for item in self:
            s += str(item)+'\n' #uses elements __repr__ function
        s += self.name+ ': line=('

        s += ', '.join([item.name for item in self]) + ');'
        s = '\n\t'.join(_textwrap.wrap(s))
        s += "\n"
        return s

    def DefineConstituentElements(self):
        """
        Return a string that contains the lines required
        to define each element in the :class:`Line`.

        Example using predefined Elements name 'd1' and 'q1':

        >>> l = Line([d1,q1])
        >>> f = open("file.txt", "w")
        >>> f.write(l.DefineConsituentElements())
        >>> f.close()
        """
        s = ''
        for item in self:
            s += str(item) #uses elements __repr__ function
        return s
class Machine(object) :

    _outer_allowed_keys = ["outerHorizontalSize", "outerVerticalSize","outerMaterial"]
    _beampipe_allowed_keys = ["vacuumMaterial", "beampipeMaterial","beampipeRadius", "beampipeThickness",
                              "e1", "e2"]
    _rbend_allowed_keys = ["angle"]
    _sbend_allowed_keys = ["angle"]
    _tiltshift_allowed_keys = ["offsetX", "offsetY", "tilt"]
    _quadrupole_allowed_keys = ["k1"]
    _target_allowed_keys = ["material","horizontalWidth","verticalWidth","apertureType"]
    _rcol_allowed_keys = ["xsize", "ysize", "material", "horizontalWidth"]
    _ecol_allowed_keys = ["xsize", "ysize", "material", "horizontalWidth"]
    _jcol_allowed_keys = ["xsize","ysize","material","xsizeLeft","xsizeRight","jawTiltLeft", "jwaTiltRight","horizontalWidth", "colour"]
    _customg4_allowed_keys = ["customLV","convertMaterials"]
    _customg4file_allowed_keys = ["geometryFile","lvName"]
    _customfluka_allowed_keys = ["customOuterBodies", "customRegions", "flukaRegistry"]
    _customflukafile_allowed_keys = ["geometryFile", "customOuterBodies", "customRegions"]
    _sampler_plane_allowed_keys = ["samplerDiameter", "samplerMaterial", "samplerThickness"]

    def __init__(self, bakeTransforms = True):

        # options (a.k.a defaults)
        self.options = _Options()

        self.elements = {}
        self.prototypes = {}
        self.sequence = []
        self.lenint    = [] # array of length upto a sequence element
        self.midrotationint = [] # rotation compounded
        self.endrotationint = [] # rotation compounded
        self.endint = [] # end point tranformed
        self.midint = [] # mid point transformed
        self.length = 0
        self.maxx = 0.0
        self.maxy = 0.0
        self.maxz = 0.0

        self.lengthsafety = 1e-3
        self.g4registry = _pyg4.geant4.Registry()
        self.flukaregistry = _pyg4.fluka.FlukaRegistry()
        self.flukanamecount = 0

        # title/global/defaults/beam/scorers etc
        self.title = None
        self.fglobal = None
        self.defaults = None
        self.beam = None
        self.randomiz = None
        self.start = None
        self.userdump = None

        # element to book-keeping-dict information
        self.elementBookkeeping = _defaultdict()

        # persistent book keeping
        self.nameRegion = {}
        self.regionnumber_regionname = {}
        self.regionname_regionnumber = {}
        self.volume_regionname = {}
        self.regionname_volume = {}

        self.verbose = True

        self.bakeTransforms = bakeTransforms

    def __iter__(self):
        self._iterindex = -1
        return self

    def __next__(self):
        if self._iterindex == len(self.sequence)-1:
            raise StopIteration
        self._iterindex += 1
        return self.elements[self.sequence[self._iterindex]]

    next = __next__

    def __getitem__(self,name):
        if _IsFloat(name):
            return self.elements[self.sequence[name]]
        else:
            return self.elements[name]

    def __len__(self):
        print('Number of unique elements:      ',len(self.elements.keys()))
        print('Number of elements in sequence: ',len(self.sequence))
        return len(self.sequence)

    def __repr__(self):
        s = ''
        s += 'pyflubl.Builder.Machine instance\n'
        s += str(len(self.sequence)) + ' items in sequence\n'
        s += str(len(self.elements)) + ' unique elements defined\n'
        return s

    def Append(self, item, addToSequence=True):
        if not isinstance(item, (Element, Line)):
            msg = "Only Elements or Lines can be added to the machine"
            raise TypeError(msg)
        elif item.name not in list(self.elements.keys()):
            #hasn't been used before - define it
            if type(item) is Line:
                for element in item:
                    self.Append(item)
            else:
                self.elements[item.name] = item
        else:
            if self.verbose:
                print("Element of name: ",item.name," already defined, simply adding to sequence")

        # add to the sequence - optional as we may be appending a parent definition to the list
        # of objects to write before the main definitions.
        if addToSequence:
            self.sequence.append(item.name)
            self.length += item.length
            self.lenint.append(self.length)

            [midrotation, endrotation, delta] = _CalculateElementTransformation(item)

            if len(self.midrotationint) == 0 :
                self.midrotationint.append(midrotation)
                self.endrotationint.append(endrotation)
                self.midint.append(delta/2)
                self.endint.append(delta)
            else :
                self.midrotationint.append(midrotation @ self.endrotationint[-1])
                self.endrotationint.append(endrotation @ self.endrotationint[-1])
                self.midint.append(self.endint[-1] + self.midrotationint[-1] @ delta/2)
                self.endint.append(self.endint[-1] + self.midrotationint[-1] @ delta)

    def AddElement(self, item):

        if item is not Element :
            msg = "Only Elements or Lines can be added to the machine"
            raise TypeError(msg)

        self.Append(item)
    def AddSplit(self):
        pass

    def AddJoin(self):
        pass

    def AddDrift(self,name, length, **kwargs):
        self._CheckElementKwargs(kwargs, self._beampipe_allowed_keys + self._outer_allowed_keys)
        e = Element(name=name, category="drift", length=length, **kwargs)
        self.Append(e)

    def AddRBend(self, name, length,  **kwargs):
        self._CheckElementKwargs(kwargs,
                                 self._beampipe_allowed_keys + \
                                 self._outer_allowed_keys + \
                                 self._rbend_allowed_keys)
        e = Element(name=name, category="rbend", length=length, **kwargs)
        self.Append(e)

    def AddSBend(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,
                                 self._beampipe_allowed_keys + \
                                 self._outer_allowed_keys + \
                                 self._sbend_allowed_keys)
        e = Element(name=name, category="sbend", length = length, **kwargs)
        self.Append(e)

    def AddSBendSplit(self, name, length, nsplit=10, **kwargs):
        angle = kwargs.pop('angle')/nsplit
        length = length/nsplit

        for i in range(0,nsplit):
            self.AddSBend(name+"_split_"+str(i), length, angle = angle, **kwargs)


    def AddQuadrupole(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,
                                 self._beampipe_allowed_keys + \
                                 self._outer_allowed_keys + \
                                 self._tiltshift_allowed_keys + \
                                 self._quadrupole_allowed_keys)

        e = Element(name=name, category="quadrupole", length = length, **kwargs)
        self.Append(e)


    def AddTarget(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,
                                 self._outer_allowed_keys + \
                                 self._tiltshift_allowed_keys + \
                                 self._target_allowed_keys)

        e = Element(name=name, category="target", length = length, **kwargs)
        self.Append(e)

    def AddRCol(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,
                                 self._outer_allowed_keys + \
                                 self._tiltshift_allowed_keys + \
                                 self._rcol_allowed_keys)

        e = Element(name=name, category="rcol", length = length, **kwargs)
        self.Append(e)

    def AddECol(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,
                                 self._outer_allowed_keys + \
                                 self._tiltshift_allowed_keys + \
                                 self._ecol_allowed_keys)

        e = Element(name=name, category="ecol", length = length, **kwargs)
        self.Append(e)

    def AddJCol(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,
                                 self._outer_allowed_keys + \
                                 self._tiltshift_allowed_keys + \
                                 self._jcol_allowed_keys)

        e = Element(name=name, category="jcol", length = length, **kwargs)
        self.Append(e)


    def AddGap(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,self._outer_allowed_keys)

        e = ElementGap(name, length)
        self.Append(e)

    def AddCustomG4(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,self._customg4_allowed_keys)

        e = ElementCustomG4(name, length, containerLV = kwargs['customLV'], convertMaterials=kwargs['convertMaterials'])
        self.Append(e)

    def AddCustomG4File(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,self._customg4file_allowed_keys)

        geometry_file = kwargs['geometryFile']
        lv_name = kwargs['lvName']

        # registry for converter
        g4registry = self._GetRegistry(True)

        # load file
        reader = _pyg4.gdml.Reader(geometry_file, registryIn = g4registry)
        lv = g4registry.logicalVolumeDict[lv_name]

        self.AddCustomG4(name,length, customLV = lv, convertMaterials = True)

    def AddCustomFluka(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,self._customfluka_allowed_keys)

        e = ElementCustomFluka(name, length,
                               customOuterBodies = kwargs['customOuterBodies'],
                               customRegions = kwargs['customRegions'],
                               flukaRegistry = kwargs['flukaRegistry'])
        self.Append(e)

    def AddCustomFlukaFile(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs,self._customflukafile_allowed_keys)


        geometry_file = kwargs['geometryFile']
        outer_bodies = kwargs['customOuterBodies']
        region_names = kwargs['customRegions']

        reader = _pyg4.fluka.Reader(geometry_file)
        registry = reader.getRegistry()

        outer_bodies = [registry.bodyDict[k] for k in outer_bodies.split()]
        regions = [registry.regionDict[k] for k in region_names.split()]

        self.AddCustomFluka(name,length,
                            customOuterBodies = outer_bodies,
                            customRegions = regions,
                            flukaRegistry = registry)

    def AddLatticeInstance(self, name, prototypeName):
        e = Element(name=name,
                    category="lattice_instance",
                    length=self.prototypes[prototypeName].length,
                    prototypeName=prototypeName)
        self.Append(e)

    def AddLatticePrototype(self, name, length, **kwargs):
        e = Element(name=name,
                    category="lattice_prototype",
                    length = length,
                    **kwargs)
        # save in prototype dict
        # transformation to be populated when built
        self.prototypes[name] = {"element":e, "rotation":None, "translation":None}


    def AddScoringHistogram(self):
        pass

    def AddScoringMesh(self):
        pass

    def AddSamplerPlane(self, name, length, **kwargs):
        self._CheckElementKwargs(kwargs, self._sampler_plane_allowed_keys)
        e = Element(name=name, category="sampler_plane", length = length, **kwargs)
        self.Append(e)

    def AddTitle(self, title):
        self.title = title

    def AddGlobal(self, fglobal):
        self.fglobal = fglobal

    def AddDefaults(self, defaults):
        self.defaults = defaults

    def AddBeam(self, beam):
        self.beam = beam

    def AddRandomiz(self, randomiz):
        self.randomiz = randomiz

    def AddStart(self, start):
        self.start = start

    def AddUserdump(self, userdump):
        self.userdump = userdump

    def _MakeBookkeepingInfo(self):

        self.finished = True
        # region number to name
        for i, r in enumerate(self.flukaregistry.regionDict) :

            self.regionnumber_regionname[i+1] = self.flukaregistry.regionDict[r].name
            self.regionname_regionnumber[self.flukaregistry.regionDict[r].name] = i+1

            self.volume_regionname[self.flukaregistry.regionDict[r].comment] = self.flukaregistry.regionDict[r].name
            self.regionname_volume[self.flukaregistry.regionDict[r].name] = self.flukaregistry.regionDict[r].comment


    def _WriteBookkeepingInfo(self, fileName="output.json", pretty=True):

        if not self.finished :
            self._makeBookkeepingInfo()

        jsonDumpDict = _defaultdict()
        jsonDumpDict["elements"] = self.elementBookkeeping
        jsonDumpDict["regionname_regionnumber"] = self.regionname_regionnumber
        jsonDumpDict["regionnumber_regionname"] = self.regionnumber_regionname

        if not pretty :
            with open(fileName, "w") as f:
                _json.dump(jsonDumpDict,f)
        else :
            # write json to file with human-friendly formatting
            pretty_json_str = _pprint.pformat(jsonDumpDict, compact=True).replace("'", '"')

            with open(fileName, 'w') as f:
                f.write(pretty_json_str)

    def Write(self, filename):

        freg = self.MakeFlukaModel()

        flukaINPFileName = filename+".inp"
        geant4GDMLFileName = filename+".gdml"
        bookkeepignFileName = filename+".json"

        if self.title:
            self.title.AddRegistry(freg)
        if self.fglobal:
            self.fglobal.AddRegistry(freg)
        if self.defaults :
            self.defaults.AddRegistry(freg)
        if self.beam :
            self.beam.AddRegistry(freg)
        if self.randomiz :
            self.randomiz.AddRegistry(freg)
        if self.start :
            self.start.AddRegistry(freg)
        if self.userdump :
            self.userdump.AddRegistry(freg)

        fw = _pyg4.fluka.Writer()
        fw.addDetector(self.flukaregistry)
        fw.write(flukaINPFileName)

        gw = _pyg4.gdml.Writer()
        gw.addDetector(self.g4registry)
        gw.write(geant4GDMLFileName)

        self._WriteBookkeepingInfo(bookkeepignFileName)

    def CheckModel(self):
        print('CheckModel')
        print('Number of elements',len(self.elements))
        print('Number of mid rotations',len(self.midrotationint))
        print('Number of end rotations',len(self.endrotationint))

        for iElement in range(0,len(self.elements)) :
            elementName = list(self.elements.keys())[iElement]
            element = self.elements[elementName]
            # print(element.category)

    def MakeFlukaModel(self):

        # initial world size
        extent = self._CalculateModelExtent()

        # sizes in cm
        xmax = max(abs(extent[0][0]), abs(extent[1][0]))*100 + 1000
        ymax = max(abs(extent[0][1]), abs(extent[1][1]))*100 + 1000
        zmax = max(abs(extent[0][2]), abs(extent[1][2]))*100 + 1000

        # make world region and surrounding black body
        self.MakeFlukaInitialGeometry(worldsize=[xmax,ymax,zmax])
        self.MakeGeant4InitialGeometry(worldsize=[2*xmax*10, 2*ymax*10, 2*zmax*10])

        # fix faces of elements
        self._FixElementFaces(view=False)

        # make lattice prototypes
        for prototype in self.prototypes :
            pass

        # loop over elements in sequence
        for s,r,t in zip(self.sequence,self.midrotationint, self.midint) :
            e = self.elements[s]
            self.ElementFactory(e,r,t)

        # make book keeping info
        self._MakeBookkeepingInfo()

        return self.flukaregistry

    def ElementFactory(self, e, r, t,
                       g4add = True,
                       fc = True):
        if e.category == "drift":
            return self.MakeFlukaBeamPipe1(name=e.name, element=e,
                                           rotation=r, translation=t * 1000,
                                           geant4RegistryAdd=g4add, flukaConvert=fc)
        elif e.category == "rbend":
            return self.MakeFlukaRBend(name=e.name, element=e,
                                       rotation=r, translation=t * 1000,
                                        geant4RegistryAdd=g4add, flukaConvert=fc)
        elif e.category == "sbend":
            return self.MakeFlukaSBend(name=e.name, element=e,
                                       rotation=r, translation=t * 1000,
                                        geant4RegistryAdd=g4add, flukaConvert=fc)
        elif e.category == "quadrupole":
            return self.MakeFlukaQuadrupole(name=e.name, element=e,
                                            rotation=r, translation=t * 1000,
                                            geant4RegistryAdd=g4add, flukaConvert=fc)
        elif e.category == "target" :
            return self.MakeFlukaTarget(name=e.name, element=e,
                                        rotation=r, translation=t * 1000,
                                        geant4RegistryAdd=g4add, flukaConvert=fc)
        elif e.category == "rcol" :
            return self.MakeFlukaRCol(name=e.name, element=e,
                                      rotation=r, translation=t * 1000,
                                      geant4RegistryAdd=g4add, flukaConvert=fc)
        elif e.category == "ecol" :
            return self.MakeFlukaECol(name=e.name, element=e,
                                      rotation=r, translation=t * 1000,
                                      geant4RegistryAdd=g4add, flukaConvert=fc)
        elif e.category == "jcol" :
            return self.MakeFlukaJCol(name=e.name, element=e,
                                      rotation=r, translation=t * 1000,
                                      geant4RegistryAdd=g4add, flukaConvert=fc)
        elif e.category == "gap" :
            return self.MakeFlukaGap(name=e.name, element=e,
                                     rotation=r, translation=t * 1000,
                                     geant4RegistryAdd=g4add, flukaConvert=fc)
        elif e.category == "customG4":
            return self.MakeFlukaCustomG4(name=e.name, element=e,
                                          rotation=r, translation=t * 1000,
                                          geant4RegistryAdd=g4add, flukaConvert=fc,
                                          convertMaterials=e.convertMaterials)
        elif e.category == "customFluka":
            return self.MakeFlukaCustomFluka(name=e.name, element=e,
                                             rotation=r, translation=t * 1000,
                                             flukaBuild=fc)
        elif e.category == "sampler_plane":
            return self.MakeFlukaSampler(name=e.name, element=e,
                                         rotation=r, translation=t * 1000,
                                         geant4RegistryAdd=g4add, flukaConvert=fc)
        elif e.category == "lattice_instance":
            return self.MakeFlukaLatticeInstance(name=e.name, element=e,
                                                 rotation=r, translation=t * 1000,
                                                 geant4RegistryAdd=g4add, flukaConvert=fc)
        else :
            print("ElementFactory not implemented")
            return None

    def MakeGeant4InitialGeometry(self, worldsize = [5000, 5000, 5000], worldMaterial = "G4_AIR"):
        worldSolid = _pyg4.geant4.solid.Box("world",worldsize[0], worldsize[1], worldsize[2], self.g4registry)
        self.worldLogical = _pyg4.geant4.LogicalVolume(worldSolid, worldMaterial, "worldLogical", self.g4registry)
        self.g4registry.setWorldVolume(self.worldLogical)

    def MakeFlukaInitialGeometry(self, worldsize = [250, 250, 250], worldmaterial = "AIR"):
        blackbody = _pyg4.fluka.RPP("BLKBODY",
                               -2*worldsize[0],2*worldsize[0],
                               -2*worldsize[1],2*worldsize[1],
                               -2*worldsize[2],2*worldsize[2],
                               transform=_rotoTranslationFromTra2("BBROTDEF",[[0,0,0],[0,0,0]],
                                                                  flukaregistry=self.flukaregistry),
                               flukaregistry=self.flukaregistry)

        worldbody = _pyg4.fluka.RPP("WORLD",
                               -1.5*worldsize[0],1.5*worldsize[0],
                               -1.5*worldsize[1],1.5*worldsize[1],
                               -1.5*worldsize[2],1.5*worldsize[2],
                               transform=_rotoTranslationFromTra2("BBROTDEF",[[0,0,0],[0,0,0]],
                                                                  flukaregistry=self.flukaregistry),
                               flukaregistry=self.flukaregistry)

        self.blackbodyzone = _pyg4.fluka.Zone()
        self.worldzone     = _pyg4.fluka.Zone()

        self.blackbodyzone.addIntersection(blackbody)
        self.blackbodyzone.addSubtraction(worldbody)

        self.worldzone.addIntersection(worldbody)

        self.blackbodyregion = _pyg4.fluka.Region("BLKHOLE")
        self.blackbodyregion.addZone(self.blackbodyzone)
        self.flukaregistry.addRegion(self.blackbodyregion)
        self.flukaregistry.addMaterialAssignments("BLCKHOLE",
                                                  "BLKHOLE")

        self.worldregion = _pyg4.fluka.Region("WORLD")
        self.worldregion.addZone(self.worldzone)
        self.flukaregistry.addRegion(self.worldregion)
        self.flukaregistry.addMaterialAssignments(worldmaterial,
                                                  "WORLD")

    def MakeFlukaGenericElementGeometry(self,
                                        name,
                                        length,
                                        geometry_bp,
                                        geometry_magnet,
                                        transform = _np.array([[1,0,0,0],
                                                               [0,1,0,0],
                                                               [0,0,1,0],
                                                               [0,0,0,1]])):
        pass

    def _MakeFlukaComponentCommonG4(self, name, containerLV, containerPV, flukaConvert, rotation, translation, category,
                                  convertMaterials = False):
        # convert materials
        if convertMaterials:
            print("_MakeFlukaComponentCommon> convertMaterials")
            materialNameSet = containerLV.makeMaterialNameSet()
            self._MakeFlukaMaterials(list(materialNameSet))

        # convert geometry
        if flukaConvert:
            flukaouterregion, self.flukanamecount = _geant4PhysicalVolume2Fluka(containerPV,
                                                                                mtra=rotation,
                                                                                tra=translation,
                                                                                flukaRegistry=self.flukaregistry,
                                                                                flukaNameCount=self.flukanamecount,
                                                                                bakeTransforms=self.bakeTransforms)

            # cut volume out of mother zone
            for daughterzones in flukaouterregion.zones:
                self.worldzone.addSubtraction(daughterzones)

        # make bookkeeping information
        if name not in self.elementBookkeeping :
            self.elementBookkeeping[name] = {}

        self.elementBookkeeping[name]['category'] = category

        # needed to book keep potentially deep lv-pv constructions in conversion
        physicalVolumeNames = containerLV.makeLogicalPhysicalNameSets()[1]
        physicalVolumeNames.add(containerPV.name)
        self.elementBookkeeping[name]['physicalVolumes'] = list(physicalVolumeNames)
        try:
            self.elementBookkeeping[name]['flukaRegions'] = [self.flukaregistry.PhysVolToRegionMap[pv] for pv in
                                                             self.elementBookkeeping[name]['physicalVolumes']]
        except KeyError:
            pass

        self.elementBookkeeping[name]['rotation'] = rotation.tolist()
        self.elementBookkeeping[name]['translation'] = translation.tolist()

        # make transformed mesh for overlaps
        outerMesh = self._MakePlacedMeshFromPV(containerPV)
        return {"placedmesh": outerMesh}


    def _MakeFlukaComponentCommonFluka(self, name, regionNames, rotation, translation, category) :

        # make bookkeeping information
        if name not in self.elementBookkeeping :
            self.elementBookkeeping[name] = {}

        self.elementBookkeeping[name]['flukaRegions'] = regionNames
        self.elementBookkeeping[name]['category'] = category
        self.elementBookkeeping[name]['rotation'] = rotation.tolist()
        self.elementBookkeeping[name]['translation'] = translation.tolist()

    def MakeFlukaBeamPipe(self, name, element,
                          rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                          translation = _np.array([0,0,0]),
                          outer=None,
                          geant4RegistryAdd = False,
                          flukaConvert = True):

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)
        g4material = self._GetDictVariable(element,"beampipeMaterial","Temp")
        beampipeRadius = self._GetDictVariable(element,"beampipeRadius",30)
        beampipeThickness = self._GetDictVariable(element,"beampipeThickness",5)
        e1 = self._GetDictVariable(element,"e1",0)
        e2 = self._GetDictVariable(element,"e2",0)

        g4registry = self._GetRegistry(geant4RegistryAdd)

        # make tubs of correct size
        bpoutersolid    = _pyg4.geant4.solid.Tubs(name+"_outer_solid",
                                                  0,beampipeRadius+beampipeThickness+self.lengthsafety,length,
                                                  0, _np.pi*2, g4registry)
        bpouterlogical  = _pyg4.geant4.LogicalVolume(bpoutersolid,g4material,name+"_outer_lv",g4registry)
        bpouterphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation)),
                                                                    translation,
                                                                    bpouterlogical,
                                                                    name+"_outer_pv",
                                                                    self.worldLogical,g4registry)

        # make actual beampipe
        bpsolid = _pyg4.geant4.solid.CutTubs(name+"_bp_solid",
                                             beampipeRadius, beampipeRadius+beampipeThickness, length,
                                             0, _np.pi*2, [0,0,-1],[0,0,1],g4registry)
        bplogical  = _pyg4.geant4.LogicalVolume(bpsolid,g4material,name+"_bp_lv",g4registry)
        bpphysical  = _pyg4.geant4.PhysicalVolume([0,0,0],[0,0,0],bplogical,name+"_bp_pv",bpouterlogical,g4registry)


        return self._MakeFlukaComponentCommonG4(name,bpouterlogical, bpouterphysical, flukaConvert,
                                              rotation, translation, "drift")

    def MakeFlukaBeamPipe1(self, name, element,
                          rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                          translation = _np.array([0,0,0]),
                          geant4RegistryAdd = False,
                          flukaConvert = True):

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        vacuumMaterial = self._GetDictVariable(element, "vacuumMaterial",  self.options.vacuumMaterial)

        outerHorizontalSize = self._GetDictVariable(element, "outerHorizontalSize", self.options.outerHorizontalSize)
        outerVerticalSize = self._GetDictVariable(element, "outerVerticalSize", self.options.outerVerticalSize)
        outerMaterial = self._GetDictVariable(element, "outerMaterial",self.options.outerMaterial)

        beampipeMaterialName = self._GetDictVariable(element,"beampipeMaterial",self.options.beampipeMaterial)
        beampipeRadius = self._GetDictVariable(element,"beampipeRadius",self.options.beampipeRadius)
        beampipeThickness = self._GetDictVariable(element,"beampipeThickness",self.options.beampipeThickness)

        e1 = self._GetDictVariable(element,"e1",0)
        e2 = self._GetDictVariable(element,"e2",0)

        g4registry = self._GetRegistry(geant4RegistryAdd)

        # make fake geant4 materials for conversion
        beampipeMaterial = _pyg4.geant4.MaterialSingleElement(name=beampipeMaterialName, atomic_number=1, atomic_weight=1, density=1)
        outerMaterial    = _pyg4.geant4.MaterialSingleElement(name=outerMaterial, atomic_number=1, atomic_weight=1, density=1)
        vacuumMaterial   = _pyg4.geant4.MaterialSingleElement(name=vacuumMaterial, atomic_number=1, atomic_weight=1, density=1)

        # make tubs of outer size
        bpoutersolid    = self._MakeGeant4GenericTrap(name,length, outerHorizontalSize/2, outerVerticalSize/2, -e1, e2, g4registry)
        bpouterlogical  = _pyg4.geant4.LogicalVolume(bpoutersolid,outerMaterial,name+"_outer_lv",g4registry)
        bpouterphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation @ _tbxyz2matrix([0,0,-_np.pi/2]) @ _tbxyz2matrix([0,-_np.pi/2,0]))),
                                                      translation,
                                                      bpouterlogical,
                                                      name+"_outer_pv",
                                                      self.worldLogical,
                                                      g4registry)

        # make actual beampipe
        bpsolid = _pyg4.geant4.solid.CutTubs(name+"_bp_solid",
                                             beampipeRadius, beampipeRadius+beampipeThickness, length,
                                             0, _np.pi*2,
                                             _tbxyz2matrix([0,e1,0]) @ _np.array([0,0,-1]),
                                             _tbxyz2matrix([0,-e2,0]) @ _np.array([0,0,1]),
                                             g4registry)
        bplogical  = _pyg4.geant4.LogicalVolume(bpsolid,beampipeMaterial,name+"_bp_lv",g4registry)
        bpphysical  = _pyg4.geant4.PhysicalVolume([0,-_np.pi/2,-_np.pi/2],[0,0,0],bplogical,name+"_bp_pv",bpouterlogical,g4registry)

        vacsolid = _pyg4.geant4.solid.CutTubs(name+"_vac_solid",
                                             0, beampipeRadius, length,
                                             0, _np.pi*2,
                                             _tbxyz2matrix([0,e1,0]) @ _np.array([0,0,-1]),
                                             _tbxyz2matrix([0,-e2,0]) @ _np.array([0,0,1]),
                                             g4registry)
        vaclogical  = _pyg4.geant4.LogicalVolume(vacsolid,vacuumMaterial,name+"_cav_lv",g4registry)
        vacphysical  = _pyg4.geant4.PhysicalVolume([0,-_np.pi/2,-_np.pi/2],[0,0,0],vaclogical,name+"_vac_pv",bpouterlogical,g4registry)

        rotation = rotation @ _tbxyz2matrix([0, 0, -_np.pi / 2]) @ _tbxyz2matrix([0, -_np.pi / 2, 0])

        return self._MakeFlukaComponentCommonG4(name,bpouterlogical, bpouterphysical, flukaConvert,
                                              rotation, translation, "drift")

    def MakeFlukaRectangularStraightOuter(self, straight_x_size, straight_y_size, length, bp_outer_radius = 1, bp_inner_radius = 2, bp_material = "AIR", transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaCircularStraightOuter(self, straight_radius, length, bpOuterRadius = 1, bp_inner_radius = 2, bp_material = "AIR", transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaBendOuter(self, bendXSize, bendYSize, length, angle, bp_outer_radius = 1, bp_inner_radius = 2, bp_material = "AIR", transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaRBend(self, name, element,
                       rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                       translation = _np.array([0,0,0]),
                       geant4RegistryAdd = True,
                       flukaConvert = True) :

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)
        angle = self._GetDictVariable(element,"angle",0)

        outerHorizontalSize = self._GetDictVariable(element, "outerHorizontalSize", self.options.outerHorizontalSize)
        outerVerticalSize = self._GetDictVariable(element, "outerVerticalSize", self.options.outerVerticalSize)
        outerMaterialName = self._GetDictVariable(element,"outerMaterial",self.options.outerMaterial)

        g4registry = self._GetRegistry(geant4RegistryAdd)

        # make fake geant4 materials for conversion
        outerMaterial    = _pyg4.geant4.MaterialSingleElement(name=outerMaterialName, atomic_number=1, atomic_weight=1, density=1)

        # make box of correct size
        outersolid    = _pyg4.geant4.solid.Box(name+"_outer_solid",outerHorizontalSize,outerVerticalSize, length, g4registry)
        outerlogical  = _pyg4.geant4.LogicalVolume(outersolid,outerMaterial,name+"_outer_lv",g4registry)
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz( _np.linalg.inv(rotation)),
                                                    translation,
                                                    outerlogical,name+"_outer_pv",
                                                    self.worldLogical,
                                                    g4registry)

        # make beampipe
        beampipelogical = self._MakeGeant4BeamPipe(name+"bp",element,g4registry)
        beampipephysical  = _pyg4.geant4.PhysicalVolume([0,0,0],
                                                        [0,0,0],
                                                        beampipelogical,
                                                        name+"_bp_pv",
                                                        outerlogical,
                                                        g4registry)

        return self._MakeFlukaComponentCommonG4(name,outerlogical, outerphysical, flukaConvert,
                                              rotation, translation, "rbend")

    def MakeFlukaSBend(self, name, element,
                       rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                       translation = _np.array([0,0,0]),
                       geant4RegistryAdd = False,
                       flukaConvert = True):

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)
        angle = self._GetDictVariable(element,"angle",0)

        outerHorizontalSize = self._GetDictVariable(element, "outerHorizontalSize", self.options.outerHorizontalSize)
        outerVerticalSize = self._GetDictVariable(element, "outerVerticalSize", self.options.outerVerticalSize)
        outerMaterialName = self._GetDictVariable(element,"outerMaterial",self.options.outerMaterial)

        g4registry = self._GetRegistry(geant4RegistryAdd)

        # make fake geant4 materials for conversion
        outerMaterial    = _pyg4.geant4.MaterialSingleElement(name=outerMaterialName, atomic_number=1, atomic_weight=1, density=1)

        dz = 2*length/angle*_np.sin(angle/2)

        # make trap of correct size
        outersolid    = self._MakeGeant4GenericTrap(name,dz, outerHorizontalSize/2, outerVerticalSize/2, -angle/2, angle/2, g4registry)
        outerlogical  = _pyg4.geant4.LogicalVolume(outersolid,outerMaterial,name+"_outer_lv",g4registry)
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_tbxyz2matrix([_np.pi/2,0,0]) @ _np.linalg.inv(_tbxyz2matrix([0,-_np.pi/2,0]) @ rotation)),
                                                    translation,
                                                    outerlogical,name+"_outer_pv",
                                                    self.worldLogical,
                                                    g4registry)

        # make beampipe
        elementCopy = _copy.deepcopy(element)
        elementCopy.length= dz/1000.0
        elementCopy['e1'] = angle/2
        elementCopy['e2'] = angle/2
        beampipelogical = self._MakeGeant4BeamPipe(name+"bp",elementCopy,g4registry)
        beampipephysical  = _pyg4.geant4.PhysicalVolume([0,-_np.pi/2,-_np.pi/2],
                                                        [0,0,0],
                                                        beampipelogical,
                                                        name+"bp_pv",
                                                        outerlogical,
                                                        g4registry)


        rotation = rotation @ _tbxyz2matrix([0,0,-_np.pi/2]) @ _tbxyz2matrix([0,_np.pi/2,0])

        ret_dict =  self._MakeFlukaComponentCommonG4(name,outerlogical, outerphysical, flukaConvert,
                                                     rotation, translation, "sbend")

        # make field
        rho = length/(2*_np.sin(angle/2.))
        b_field = self._CalculateDipoleFieldStrength(self.beam.energy, rho)

        # make field transform

        # assign field to region(s)



        return ret_dict
    def MakeFlukaQuadrupole(self, name, element,
                            rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                            translation = _np.array([0,0,0]),
                            geant4RegistryAdd = False,
                            flukaConvert = True):

        quadlength = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = self._GetDictVariable(element, "outerHorizontalSize", self.options.outerHorizontalSize)
        outerVerticalSize = self._GetDictVariable(element, "outerVerticalSize", self.options.outerVerticalSize)
        outerMaterialName = self._GetDictVariable(element,"outerMaterial",self.options.outerMaterial)

        g4registry = self._GetRegistry(geant4RegistryAdd)

        # make fake geant4 materials for conversion
        outerMaterial    = _pyg4.geant4.MaterialSingleElement(name=outerMaterialName, atomic_number=1, atomic_weight=1, density=1)

        # make box of correct size
        outersolid    = _pyg4.geant4.solid.Box(name+"_solid",outerHorizontalSize,outerVerticalSize,quadlength,g4registry)
        outerlogical  = _pyg4.geant4.LogicalVolume(outersolid,outerMaterial,name+"_lv",g4registry)
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation)),
                                                      translation,
                                                      outerlogical,
                                                      name+"_pv",
                                                      self.worldLogical,
                                                      g4registry)

        # make beampipe
        beampipelogical = self._MakeGeant4BeamPipe(name+"bp",element,g4registry)
        beampipephysical  = _pyg4.geant4.PhysicalVolume([0,0,0],
                                                        [0,0,0],
                                                        beampipelogical,
                                                        name+"bp_pv",
                                                        outerlogical,
                                                        g4registry)

        return self._MakeFlukaComponentCommonG4(name,outerlogical, outerphysical, flukaConvert,
                                              rotation, translation, "quad")


    def MakeFlukaTarget(self, name, element,
                      rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                      translation = _np.array([0,0,0]),
                      geant4RegistryAdd = False,
                      flukaConvert = True):

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = self._GetDictVariable(element, "outerHorizontalSize", self.options.outerHorizontalSize)
        outerVerticalSize = self._GetDictVariable(element, "outerVerticalSize", self.options.outerVerticalSize)
        outerMaterialName = self._GetDictVariable(element,"outerMaterial",self.options.outerMaterial)

        materialName = self._GetDictVariable(element,"material","IRON")
        apertureType = self._GetDictVariable(element,"apertureType","rectangle")
        horizontalWidth = self._GetDictVariable(element,"horizontalWidth",outerHorizontalSize-5)
        verticalWidth = self._GetDictVariable(element,"verticalWidth",horizontalWidth)


        # make fake geant4 materials for conversion
        outerMaterial = _pyg4.geant4.MaterialSingleElement(name=outerMaterialName, atomic_number=1, atomic_weight=1, density=1)
        targetMaterial = _pyg4.geant4.MaterialSingleElement(name=materialName, atomic_number=1, atomic_weight=1, density=1)

        # pyg4ometry registry
        g4registry = self._GetRegistry(geant4RegistryAdd)

        # make box of correct size
        outersolid    = _pyg4.geant4.solid.Box(name+"_solid",outerHorizontalSize,outerVerticalSize,length,g4registry)
        outerlogical  = _pyg4.geant4.LogicalVolume(outersolid,outerMaterial,name+"_lv",g4registry)
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation)),
                                                      translation,
                                                      outerlogical,
                                                      name+"_pv",
                                                      self.worldLogical,
                                                      g4registry)

        if apertureType == "rectangle":
            targetsolid = _pyg4.geant4.solid.Box(name+"_target_solid",horizontalWidth, verticalWidth,length,g4registry)
        elif apertureType == "circular" or apertureType == "elliptical":
            targetsolid = _pyg4.geant4.solid.EllipticalTube(name+"_target_solid",horizontalWidth, verticalWidth,length,g4registry)
        else :
            targetsolid = _pyg4.geant4.solid.Box(name+"_target_solid",horizontalWidth, verticalWidth,length,g4registry)

        targetlogical  = _pyg4.geant4.LogicalVolume(targetsolid,targetMaterial,name+"_targe_lv",g4registry)
        targetphysical = _pyg4.geant4.PhysicalVolume([0,0,0],
                                                     [0,0,0],
                                                     targetlogical,
                                                     name+"_taget_pv",
                                                     outerlogical,
                                                     g4registry)

        return self._MakeFlukaComponentCommonG4(name,outerlogical, outerphysical, flukaConvert,
                                              rotation, translation, "target")

    def MakeFlukaRCol(self, name, element,
                      rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                      translation = _np.array([0,0,0]),
                      geant4RegistryAdd = False,
                      flukaConvert = True):

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = self._GetDictVariable(element, "outerHorizontalSize", self.options.outerHorizontalSize)
        outerVerticalSize = self._GetDictVariable(element, "outerVerticalSize", self.options.outerVerticalSize)
        outerMaterialName = self._GetDictVariable(element,"outerMaterial",self.options.outerMaterial)

        materialName = self._GetDictVariable(element,"material","IRON")
        xsize = self._GetDictVariable(element,"xsize",0)
        ysize = self._GetDictVariable(element,"ysize",0)

        horizontalWidth = self._GetDictVariable(element,"horizontalWidth",outerHorizontalSize-5)
        verticalWidth = self._GetDictVariable(element,"horizontalWidth",outerVerticalSize-5)

        # make fake geant4 materials for conversion
        outerMaterial = _pyg4.geant4.MaterialSingleElement(name=outerMaterialName, atomic_number=1, atomic_weight=1, density=1)
        collimatorMaterial = _pyg4.geant4.MaterialSingleElement(name=materialName, atomic_number=1, atomic_weight=1, density=1)
        # pyg4ometry registry
        g4registry = self._GetRegistry(geant4RegistryAdd)

        # make box of correct size
        outersolid    = _pyg4.geant4.solid.Box(name+"_solid",outerHorizontalSize,outerVerticalSize,length,g4registry)
        outerlogical  = _pyg4.geant4.LogicalVolume(outersolid,outerMaterial,name+"_lv",g4registry)
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation)),
                                                      translation,
                                                      outerlogical,
                                                      name+"_pv",
                                                      self.worldLogical,
                                                      g4registry)

        collimatorsolid1 = _pyg4.geant4.solid.Box(name+"_rcol1_solid",horizontalWidth,verticalWidth,length,g4registry)
        collimatorsolid2 = _pyg4.geant4.solid.Box(name+"_rcol2_solid",xsize,ysize,length,g4registry)

        if xsize == 0 or ysize == 0 :
            collimatorsolid = collimatorsolid1
        else :
            collimatorsolid = _pyg4.geant4.solid.Subtraction(name+"_rcol_solid",collimatorsolid1, collimatorsolid2,
                                                             [[0,0,0],[0,0,0]], g4registry)

        collimatorlogical  = _pyg4.geant4.LogicalVolume(collimatorsolid,collimatorMaterial,name+"_rcol_lv",g4registry)
        collimatorlogicalphysical = _pyg4.geant4.PhysicalVolume([0,0,0],[0,0,0],
                                                                collimatorlogical,
                                                                name+"_rcol_pv",
                                                                outerlogical,
                                                                g4registry)

        return self._MakeFlukaComponentCommonG4(name,outerlogical, outerphysical, flukaConvert,
                                              rotation, translation, "rcol")

    def MakeFlukaECol(self, name, element,
                      rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                      translation = _np.array([0,0,0]),
                      geant4RegistryAdd = False,
                      flukaConvert = True):

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = self._GetDictVariable(element, "outerHorizontalSize", self.options.outerHorizontalSize)
        outerVerticalSize = self._GetDictVariable(element, "outerVerticalSize", self.options.outerVerticalSize)
        outerMaterialName = self._GetDictVariable(element,"outerMaterial",self.options.outerMaterial)

        materialName = self._GetDictVariable(element,"material","IRON")
        xsize = self._GetDictVariable(element,"xsize",0)
        ysize = self._GetDictVariable(element,"ysize",0)

        horizontalWidth = self._GetDictVariable(element,"horizontalWidth",outerHorizontalSize-5)
        verticalWidth = self._GetDictVariable(element,"horizontalWidth",outerVerticalSize-5)

        # make fake geant4 materials for conversion
        outerMaterial = _pyg4.geant4.MaterialSingleElement(name=outerMaterialName, atomic_number=1, atomic_weight=1, density=1)
        collimatorMaterial = _pyg4.geant4.MaterialSingleElement(name=materialName, atomic_number=1, atomic_weight=1, density=1)
        # pyg4ometry registry
        g4registry = self._GetRegistry(geant4RegistryAdd)

        # make box of correct size
        outersolid    = _pyg4.geant4.solid.Box(name+"_solid",outerHorizontalSize,outerVerticalSize,length,g4registry)
        outerlogical  = _pyg4.geant4.LogicalVolume(outersolid,outerMaterial,name+"_lv",g4registry)
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation)),
                                                      translation,
                                                      outerlogical,
                                                      name+"_pv",
                                                      self.worldLogical,
                                                      g4registry)

        collimatorsolid1 = _pyg4.geant4.solid.Box(name+"_rcol1_solid",horizontalWidth,verticalWidth,length,g4registry)
        collimatorsolid2 = _pyg4.geant4.solid.EllipticalTube(name+"_rcol2_solid",xsize,ysize,length,g4registry)

        if xsize == 0 or ysize == 0 :
            collimatorsolid = collimatorsolid1
        else :
            collimatorsolid = _pyg4.geant4.solid.Subtraction(name+"_rcol_solid",collimatorsolid1, collimatorsolid2,
                                                             [[0,0,0],[0,0,0]], g4registry)

        collimatorlogical  = _pyg4.geant4.LogicalVolume(collimatorsolid,collimatorMaterial,name+"_rcol_lv",g4registry)
        collimatorlogicalphysical = _pyg4.geant4.PhysicalVolume([0,0,0],[0,0,0],
                                                                collimatorlogical,
                                                                name+"_rcol_pv",
                                                                outerlogical,
                                                                g4registry)

        return self._MakeFlukaComponentCommonG4(name,outerlogical, outerphysical, flukaConvert,
                                              rotation, translation, "ecol")


    def MakeFlukaJCol(self, name, element,
                      rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                      translation = _np.array([0,0,0]),
                      geant4RegistryAdd = False,
                      flukaConvert = True):

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = self._GetDictVariable(element, "outerHorizontalSize", self.options.outerHorizontalSize)
        outerVerticalSize = self._GetDictVariable(element, "outerVerticalSize", self.options.outerVerticalSize)
        outerMaterialName = self._GetDictVariable(element,"outerMaterial",self.options.outerMaterial)

        materialName = self._GetDictVariable(element,"material","IRON")
        xsize = self._GetDictVariable(element,"xsize",0)
        ysize = self._GetDictVariable(element,"ysize",0)

        xsizeLeft = self._GetDictVariable(element,"xsizeLeft",0)
        xsizeRight = self._GetDictVariable(element,"xsizeRight",0)

        jawTiltLeft = self._GetDictVariable(element,"jawTiltLeft",0)
        jawTiltRight = self._GetDictVariable(element,"jawTiltRight",0)

        horizontalWidth = self._GetDictVariable(element,"horizontalWidth",outerHorizontalSize-5)
        verticalWidth = self._GetDictVariable(element,"horizontalWidth",outerVerticalSize-5)

        # make fake geant4 materials for conversion
        outerMaterial = _pyg4.geant4.MaterialSingleElement(name=outerMaterialName, atomic_number=1, atomic_weight=1, density=1)
        collimatorMaterial = _pyg4.geant4.MaterialSingleElement(name=materialName, atomic_number=1, atomic_weight=1, density=1)
        # pyg4ometry registry
        g4registry = self._GetRegistry(geant4RegistryAdd)

        # make box of correct size
        outersolid    = _pyg4.geant4.solid.Box(name+"_solid",outerHorizontalSize,outerVerticalSize,length,g4registry)
        outerlogical  = _pyg4.geant4.LogicalVolume(outersolid,outerMaterial,name+"_lv",g4registry)
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation)),
                                                      translation,
                                                      outerlogical,
                                                      name+"_pv",
                                                      self.worldLogical,
                                                      g4registry)

        # default left size
        leftwidth = horizontalWidth / 2 - xsize / 2
        # default right size
        rightwidth = leftwidth

        leftcentre = xsize + leftwidth/2
        rightcentre = -xsize - rightwidth/2

        print(horizontalWidth, xsize, leftwidth, rightwidth, leftcentre, rightcentre)

        if xsizeLeft != 0:
            leftwidth = horizontalWidth / 2
            leftcentre = xsizeLeft + leftwidth / 2

        if xsizeRight != 0:
            rightwidth = horizontalWidth / 2
            rightcentre = - xsizeRight - rightwidth / 2

        if jawTiltLeft == 0 and jawTiltRight == 0 :
            leftsolid = _pyg4.geant4.solid.Box(name + "_jcol_left_solid", leftwidth, verticalWidth, length,
                                               g4registry)
            rightsolid = _pyg4.geant4.solid.Box(name + "_jcol_right_solid", rightwidth, verticalWidth, length,
                                               g4registry)

            rightlogical  = _pyg4.geant4.LogicalVolume(rightsolid,collimatorMaterial,name+"_rcol_right_lv",g4registry)
            rightphysical = _pyg4.geant4.PhysicalVolume([0,0,0],[rightcentre,0,0],
                                                         rightlogical,
                                                         name+"_jcol_right_pv",
                                                         outerlogical,
                                                         g4registry)

            leftlogical  = _pyg4.geant4.LogicalVolume(leftsolid,collimatorMaterial,name+"_rcol_left_lv",g4registry)
            leftphysical = _pyg4.geant4.PhysicalVolume([0,0,0],[leftcentre,0,0],
                                                       leftlogical,
                                                       name+"_jcol_left_pv",
                                                       outerlogical,
                                                       g4registry)

        else :
            # TODO complete tilted RCol and zero gap
            pass




        return self._MakeFlukaComponentCommonG4(name,outerlogical, outerphysical, flukaConvert,
                                              rotation, translation, "jcol")

    def MakeFlukaGap(self, name, element,
                     rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                     translation = _np.array([0,0,0]),
                     geant4RegistryAdd = False,
                     flukaConvert = True):

        # registry
        g4registry = self._GetRegistry(geant4RegistryAdd)

        # length
        length = element.length * 1000

        # outer material
        outerMaterialName = self._GetDictVariable(element,"outerMaterial",self.options.outerMaterial)
        outerMaterial = _pyg4.geant4.MaterialSingleElement(name=outerMaterialName, atomic_number=1, atomic_weight=1, density=1)

        # make box of correct size
        outersolid    = _pyg4.geant4.solid.Box(name+"_solid", 500, 500, length, g4registry)
        outerlogical  = _pyg4.geant4.LogicalVolume(outersolid, outerMaterial, name+"_lv", g4registry)
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation)),
                                                      translation,
                                                      outerlogical,
                                                      name+"_pv",
                                                      self.worldLogical,
                                                      g4registry)

        return self._MakeFlukaComponentCommonG4(name,outerlogical, outerphysical, flukaConvert,
                                              rotation, translation, "gap")

    def MakeFlukaCustomG4(self, name, element,
                          rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                          translation = _np.array([0,0,0]),
                          geant4RegistryAdd = False,
                          flukaConvert = True,
                          convertMaterials= False):

        # registry
        g4registry = self._GetRegistry(geant4RegistryAdd)

        # length
        length = element.length * 1000

        # make box of correct size
        outerlogical  = element.containerLV
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation)),
                                                      translation,
                                                      outerlogical,
                                                      name+"_pv",
                                                      self.worldLogical,
                                                      g4registry)

        return self._MakeFlukaComponentCommonG4(name,outerlogical, outerphysical, flukaConvert,
                                              rotation, translation, "gap",
                                              convertMaterials=convertMaterials)

    def MakeFlukaCustomFluka(self, name, element,
                             rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                             translation = _np.array([0,0,0]),
                             flukaBuild = True):

        regionNamesTransferred = []

        outer_bodies = element.outer_bodies
        regions = element.regions

        if flukaBuild:
            print('MakeFlukaCustomFluka')

            # cut out regions for placement
            for body in outer_bodies:
                z = _pyg4.fluka.Zone()
                z.addIntersection(body)
                self.worldzone.addSubtraction(z)

            # transfer bodies and regions to fluka registry
            for region in regions:
                regionNamesTransferred.append(region.name)

                if region.name not in self.flukaregistry.regionDict :
                    self.flukaregistry.addRegion(region)
                for zone in region.zones :
                    for body in zone.bodies() :
                        if body.name not in self.flukaregistry.bodyDict :
                            body = body._transform(rotation, translation)
                            body._scale(0.1)
                            self.flukaregistry.addBody(body)

            # transfer materials to fluka registry
            # loop over regions, find assignmas, find material
            for region in regions:
                region_name = region.name
                fluka_registry = element.fluka_registry

                mat = fluka_registry.assignmas[region.name]
                self.flukaregistry.addMaterialAssignments(mat[0],region.name)

        # loop over outer regions, form meshes and union
        first = True
        for outer_region in regions :
            if first :
                m = outer_region.mesh()
                first = False
            else :
                m.union(outer_region.mesh())

        m.scale(10,10,10)

        self._MakeFlukaComponentCommonFluka(name, regionNamesTransferred, rotation, translation, element.category)

        return {"placedmesh": m}

    # TODO remove this as custom
    def MakeFlukaGeometryPlacement(self,
                                   name,
                                   geometry,
                                   transform = _np.array([[1,0,0],[0,1,0],[0,0,1]])):
        pass

    def MakeFlukaLatticePrototype(self, name, element,
                                  rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                                  translation = _np.array([0,0,0]),
                                  geant4RegistryAdd = False, flukaConvert = True):
        pass

    def MakeFlukaLatticeInstance(self, name, element,
                                 rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                                 translation = _np.array([0,0,0]),
                                 geant4RegistryAdd = False, flukaConvert = True):
        pass

    def MakeFlukaSplit(self, length, angles = [], bp_outer_radii = [], bp_inner_radii = []):
        pass

    def MakeFlukaSampler(self, name, element,
                         rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                         translation = _np.array([0,0,0]),
                         geant4RegistryAdd = False,
                         flukaConvert = True):


        samplerLength = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)
        samplerMaterialName = self._GetDictVariable(element,"samplerMaterial","AIR")
        samplerDiameter = self._GetDictVariable(element,"samplerDiameter",2000)
        g4registry = self._GetRegistry(geant4RegistryAdd)

        # make fake geant4 materials for conversion
        samplerMaterial = _pyg4.geant4.MaterialSingleElement(name=samplerMaterialName, atomic_number=1, atomic_weight=1, density=1)

        # make box of correct size
        samplersolid    = _pyg4.geant4.solid.Box(name+"_solid",samplerDiameter,samplerDiameter,samplerLength,g4registry)
        samplerlogical  = _pyg4.geant4.LogicalVolume(samplersolid,samplerMaterial,name+"_lv",g4registry)
        samplerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation)),
                                                      translation,
                                                      samplerlogical,
                                                      name+"_pv",
                                                      self.worldLogical,
                                                      g4registry)

        return self._MakeFlukaComponentCommonG4(name,samplerlogical, samplerphysical, flukaConvert,
                                              rotation, translation, "sampler")

    def _MakeGeant4GenericTrap(self, name,
                               length = 500, xhalfwidth = 50, yhalfwidth = 50,
                               e1=0, e2=0,
                               g4registry = None):

        if not g4registry :
            g4registry = self.g4registry

        p1x = -length/2 + yhalfwidth * _np.tan(e1)
        p1y = yhalfwidth
        p2x = -length/2 - yhalfwidth * _np.tan(e1)
        p2y = -yhalfwidth
        p3x =  length/2 - yhalfwidth * _np.tan(e2)
        p3y = -yhalfwidth
        p4x =  length/2 + yhalfwidth * _np.tan(e2)
        p4y =  yhalfwidth
        p5x = p1x
        p5y = p1y
        p6x = p2x
        p6y = p2y
        p7x = p3x
        p7y = p3y
        p8x = p4x
        p8y = p4y
        z = xhalfwidth
        trapsolid    = _pyg4.geant4.solid.GenericTrap(name+"_solid",
                                                      p1x,p1y,
                                                      p2x,p2y,
                                                      p3x,p3y,
                                                      p4x,p4y,
                                                      p5x,p5y,
                                                      p6x,p6y,
                                                      p7x,p7y,
                                                      p8x,p8y,
                                                      z,g4registry)

        return trapsolid

    def _MakeGeant4BeamPipe(self, name, element, g4registry = None):

        if not g4registry:
            g4registry = self.g4registry

        length = element.length*1000
        vacuumMaterialName = self._GetDictVariable(element,"vacuumMaterial","VACUUM")
        beampipeMaterialName = self._GetDictVariable(element,"beampipeMaterial",self.options.beampipeMaterial)
        beampipeRadius = self._GetDictVariable(element,"beampipeRadius",self.options.beampipeRadius)
        beampipeThickness = self._GetDictVariable(element,"beampipeThickness",self.options.beampipeThickness)

        e1 = self._GetDictVariable(element,"e1",0)
        e2 = self._GetDictVariable(element,"e2",0)

        # fake materials
        vacuumMaterial = _pyg4.geant4.MaterialSingleElement(name=vacuumMaterialName, atomic_number=1, atomic_weight=1, density=1)
        beampipeMaterial = _pyg4.geant4.MaterialSingleElement(name=beampipeMaterialName, atomic_number=1, atomic_weight=1, density=1)

        # make actual beampipe
        bpsolid = _pyg4.geant4.solid.CutTubs(name+"_bp_solid",
                                             0, beampipeRadius+beampipeThickness, length,
                                             0, _np.pi*2,
                                             _tbxyz2matrix([0,e1,0]) @ _np.array([0,0,-1]),
                                             _tbxyz2matrix([0,-e2,0]) @ _np.array([0,0,1]),
                                             g4registry)
        bplogical  = _pyg4.geant4.LogicalVolume(bpsolid,beampipeMaterial,name+"_bp_lv",g4registry)

        vacsolid = _pyg4.geant4.solid.CutTubs(name+"_vac_solid",
                                             0, beampipeRadius, length,
                                             0, _np.pi*2,
                                             _tbxyz2matrix([0,e1,0]) @ _np.array([0,0,-1]),
                                             _tbxyz2matrix([0,-e2,0]) @ _np.array([0,0,1]),
                                             g4registry)
        vaclogical  = _pyg4.geant4.LogicalVolume(vacsolid,vacuumMaterial,name+"_cav_lv",g4registry)
        vacphysical  = _pyg4.geant4.PhysicalVolume([0,0,0],[0,0,0],vaclogical,name+"_vac_pv",bplogical,g4registry)

        return bplogical

    def _MakeFlukaMaterials(self, materials = []):
        for g4material in materials :
            if g4material not in self.flukaregistry.materialShortName :
                if type(g4material) is str :
                    g4material_name = g4material
                    g4material = _pyg4.geant4.nist_material_2geant4Material(g4material)
                    materialNameShort = "M" + format(self.flukaregistry.iMaterials, "03")
                    _geant4Material2Fluka(g4material,self.flukaregistry,materialNameShort=materialNameShort)
                    self.flukaregistry.materialShortName[g4material_name] = materialNameShort
                    self.flukaregistry.iMaterials += 1

    def _GetDictVariable(self, element, key, default):
        try :
            variable = element[key]
        except :
            variable = default

        return variable

    def _GetRegistry(self,geant4RegistryAdd = False) :
        if geant4RegistryAdd:
            g4registry = self.g4registry
        else:
            g4registry = _pyg4.geant4.Registry()

        return g4registry

    def _MakePlacedMeshFromPV(self, physVol):
        rotation = physVol.rotation.eval()
        translation = physVol.position.eval()
        mesh = physVol.logicalVolume.solid.mesh()

        aa = _tbxyz2axisangle(rotation)
        mesh.rotate(aa[0], aa[1] / _np.pi * 180.0)
        mesh.translate([translation[0], translation[1], translation[2]])

        return mesh

    def _FixElementFaces(self, view = True):

        print("_FixElementFaces>")
        if view :
            v = _pyg4.visualisation.VtkViewerNew()
            v.addAxes(2500)

        for iElement in range(0,len(self.elements)) :
            elementName = list(self.elements.keys())[iElement]
            e = self.elements[elementName]
            r = list(self.midrotationint)[iElement]
            t = list(self.midint)[iElement]

            m = self.ElementFactory(e, r, t, False, False)["placedmesh"]

            if view :
                v.addMesh(elementName, m)
                v.addInstance(elementName,
                              _np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                              _np.array([0,0,0]),
                              elementName)
                v.addVisOptions(elementName,
                                _pyg4.visualisation.VisualisationOptions(representation="wireframe", colour=[1, 1, 1]))

            for jElement in range(iElement+1,len(self.elements)) :
                jElementName = list(self.elements.keys())[jElement]
                je = self.elements[jElementName]
                jr = list(self.midrotationint)[jElement]
                jt = list(self.midint)[jElement]
                jm = self.ElementFactory(je, jr, jt, False, False)["placedmesh"]

                # check for intersection
                jinter = jm.intersect(m)

                if jinter.volume() > 0.1 :
                    if e.category == "rbend" and je.category == "drift":
                        je['e1'] = e['angle']/2
                    elif e.category == "drift" and je.category == "rbend"  and iElement != 0 :
                        e['e2'] = je['angle']/2
                    elif e.category == "drift" and je.category == "rbend"  and iElement == 0 :
                        e['e1'] = je['angle']/2

                if view:
                    v.addMesh(elementName+jElementName,jinter)
                    v.addInstance(elementName+jElementName,
                                  _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                                  _np.array([0,0,0]),
                                  elementName+jElementName)
                    v.addVisOptions(elementName+jElementName,
                                    _pyg4.visualisation.VisualisationOptions(representation="surface",
                                                                             colour=[_random.random(),_random.random(),_random.random()]))

        if view :
            v.buildPipelinesAppend()
            v.view()

        print("FixElementFaces<")

    def _MakeOffsetAndTiltTransforms(self, element, rotation, translation):
        offsetX = self._GetDictVariable(element,"offsetX",0)
        offsetY = self._GetDictVariable(element,"offsetY",0)
        tilt    = self._GetDictVariable(element,"tilt",0)

        translation = translation + _np.array([offsetX, offsetY, 0])
        rotation =  rotation @ _tbxyz2matrix([0,0,tilt])

        return rotation, translation

    def _LoadGDMLGeometry(self, element):
        geometryFile = self._GetDictVariable(element, "geometryFile", "None")

    def _CalculateDipoleFieldStrength(self, momentum, rho):
        return 3.3356*momentum / rho

    def _CalculateQuadrupoleFieldStrength(self, momentum, k1):
        return 0

    def _CalculateModelExtent(self):
        # loop over positions and find maxima
        vmin = [9e99, 9e99, 9e99]
        vmax = [-9e99, -9e99, -9e99]

        for p in self.midint :
            if p[0] < vmin[0] :
                vmin[0] = p[0]
            if p[1] < vmin[1] :
                vmin[1] = p[1]
            if p[2] < vmin[2] :
                vmin[2] = p[2]

            if p[0] > vmax[0]:
                vmax[0] = p[0]
            if p[1] > vmax[1] :
                vmax[1] = p[1]
            if p[2] > vmax[2] :
                vmax[2] = p[2]

        return [vmin,vmax]

    def _CheckElementKwargs(self, kwargs, allowed_keys):
        for key in kwargs:
            if key not in allowed_keys:
                raise TypeError(f"Unexpected keyword argument: {key}")

    def ViewGeant4(self, separateMeshes = False):
        if not separateMeshes :
            v = _pyg4.visualisation.VtkViewerNew()
            v.addLogicalVolume(self.worldLogical)
            v.buildPipelinesAppend()
            v.addAxes(2500)
            v.view()
        else :
            v = _pyg4.visualisation.VtkViewerNew()
            v.addAxes(2500)

            for s, r, t in zip(self.sequence, self.midrotationint, self.midint):
                e = self.elements[s]
                m = self.ElementFactory(e, r, t, False, False)["placedmesh"]
                v.addMesh(e.name,m)
                v.addInstance(e.name,_np.array([[1,0,0],[0,1,0],[0,0,1]]), _np.array([0,0,0]),e.name)
                v.addVisOptions(e.name, _pyg4.visualisation.VisualisationOptions(representation="surface"))
            v.buildPipelinesAppend()
            v.view()
            return v

# dynamic doc strings
Machine.AddDrift.__doc__ =  """allowed kwargs: """ + \
                            " ".join(Machine._beampipe_allowed_keys) +\
                            " " + " ".join(Machine._outer_allowed_keys)
Machine.AddRBend.__doc__ =  ("""allowed kwargs: """ + \
                            " ".join(Machine._beampipe_allowed_keys) + \
                            " " + " ".join(Machine._outer_allowed_keys) +
                             " " + " ".join(Machine._rbend_allowed_keys))
Machine.AddSBend.__doc__ =  """allowed kwargs: """ + \
                            " ".join(Machine._beampipe_allowed_keys) + \
                            " " + " ".join(Machine._outer_allowed_keys) + \
                            " " + " ".join(Machine._sbend_allowed_keys)
Machine.AddQuadrupole.__doc__ = """allowed kwargs """ + \
                                " ".join(Machine._beampipe_allowed_keys) + \
                                " " + " ".join(Machine._outer_allowed_keys) + \
                                " " + " ".join(Machine._quadrupole_allowed_keys) + \
                                " " + " ".join(Machine._tiltshift_allowed_keys)
Machine.AddTarget.__doc__ = """allowed kwargs""" \
                            " " + " ".join(Machine._outer_allowed_keys) + \
                            " " + " ".join(Machine._tiltshift_allowed_keys) + \
                            " " + " ".join(Machine._target_allowed_keys)
Machine.AddRCol.__doc__ = """allowed kwargs """ + \
                          " " + " ".join(Machine._outer_allowed_keys) + \
                          " " + " ".join(Machine._tiltshift_allowed_keys) + \
                          " " + " ".join(Machine._rcol_allowed_keys)
Machine.AddECol.__doc__ = """allowed kwargs """ + \
                          " " + " ".join(Machine._outer_allowed_keys) + \
                          " " + " ".join(Machine._tiltshift_allowed_keys) + \
                          " " + " ".join(Machine._ecol_allowed_keys)
Machine.AddJCol.__doc__ = """allowed kwargs """ + \
                          " " + " ".join(Machine._outer_allowed_keys) + \
                          " " + " ".join(Machine._tiltshift_allowed_keys) + \
                          " " + " ".join(Machine._jcol_allowed_keys)
Machine.AddGap.__doc__ = """allowed kwargs """ + \
                         " " + " ".join(Machine._outer_allowed_keys)

Machine.AddCustomG4.__doc__ = """allowed kwargs """ + \
                              " " + " ".join(Machine._customg4_allowed_keys)
Machine.AddCustomG4File.__doc__ = """allowed kwargs """ + \
                                  " " + " ".join(Machine._customg4file_allowed_keys)
Machine.AddSamplerPlane.__doc__ = """allowed kwargs: """ + \
                                  " ".join(Machine._sampler_plane_allowed_keys)
Machine.AddCustomFluka.__doc__ = """allowed kwargs: """ + \
                                  " ".join(Machine._customfluka_allowed_keys)
Machine.AddCustomFlukaFile.__doc__ = """allowed kwargs: """ + \
                                     " ".join(Machine._customflukafile_allowed_keys)