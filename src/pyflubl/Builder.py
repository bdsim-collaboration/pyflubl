try: # Deprecated, removed in Python 3.10
    from collections import MutableMapping as _MutableMapping
except ImportError: # Python 3.10 onwards.
    from collections.abc import MutableMapping as _MutableMapping
import numbers as _numbers

import numpy as _np
import json as _json
import copy as _copy
import pprint as _pprint
from collections import OrderedDict as _OrderedDict

import pyg4ometry as _pyg4
from pyg4ometry.fluka.directive import rotoTranslationFromTra2 as _rotoTranslationFromTra2
from pyg4ometry.convert.geant42Fluka import geant4PhysicalVolume2Fluka as _geant4PhysicalVolume2Fluka
from pyg4ometry.convert.geant42Fluka import geant4Material2Fluka as _geant4Material2Fluka
from pyg4ometry.transformation import matrix2tbxyz as _matrix2tbxyz
from pyg4ometry.transformation import tbxyz2matrix as _tbxyz2matrix

pyflublcategories = [
    'drift',
    'rbend',
    'sbend',
    'quadrupole',
    'sampler_plane'
    ]


def _CalculateElementTransformation(e):
    if e.category == "drift" :
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
    def __init__(self, bakeTransforms = False):
        self.elements = {}
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

        # element to book-keeping-dict information
        self.elementBookkeeping = _OrderedDict()

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
        # beampipe
        # apertureType, beampipeRadius or aper1, aper2, aper3, aper4
        # vacuumMaterial, beampipeThickness, beampipeMaterial
        e = Element(name=name, category="drift", length=length, **kwargs)
        self.Append(e)

    def AddRBend(self, name, length,  **kwargs):
        # beampipe
        # apertureType, beampipeRadius or aper1, aper2, aper3, aper4
        # vacuumMaterial, beampipeThickness, beampipeMaterial

        # sbend
        # angle, B, e1, e2, material, yokeOnInside, hStyle, k1, tilt

        e = Element(name=name, category="rbend", length=length, **kwargs)
        self.Append(e)

    def AddSBend(self, name, length, **kwargs):
        # beampipe
        # apertureType, beampipeRadius or aper1, aper2, aper3, aper4
        # vacuumMaterial, beampipeThickness, beampipeMaterial

        # sbend
        # angle, B, e1, e2, material, yokeOnInside, hStyle, k1, tilt
        e = Element(name=name, category="sbend", length = length, **kwargs)
        self.Append(e)

    def AddQuadrupole(self):
        pass

    def AddScoringHistogram(self):
        pass

    def AddScoringMesh(self):
        pass

    def AddSamplerPlane(self, name, length, **kwargs):
        e = Element(name=name, category="sampler_plane", length = length)
        self.Append(e)

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

        jsonDumpDict = _OrderedDict()
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
        bookkeepignFileName = filename+".json"

        w = _pyg4.fluka.Writer()
        w.addDetector(self.flukaregistry)
        w.write(flukaINPFileName)

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

        # make world region and surrounding black body
        self.MakeFlukaInitialGeometry()
        self.MakeGeant4InitialGeometry()

        # loop over elements in sequence
        for s,r,t in zip(self.sequence,self.midrotationint, self.midint) :
            e = self.elements[s]
            if e.category == "drift" :
                self.MakeFlukaBeamPipe1(name=e.name, element=e, rotation=r, translation=t*1000)
            elif e.category == "rbend" :
                self.MakeFlukaRBend(name=e.name, element=e, rotation=r, translation=t*1000)
            elif e.category == "sbend" :
                self.MakeFlukaSBend(name=e.name, element=e, rotation=r, translation=t*1000)
            elif e.category == "sampler_plane" :
                self.MakeFlukaSampler(name=e.name, element=e, rotation=r, translation=t*1000)

        # make book keeping info
        self._MakeBookkeepingInfo()

    def MakeGeant4InitialGeometry(self, worldsize = [5000, 5000, 5000], worldMaterial = "G4_AIR"):
        worldSolid = _pyg4.geant4.solid.Box("world",worldsize[0], worldsize[1], worldsize[2], self.g4registry)
        self.worldLogical = _pyg4.geant4.LogicalVolume(worldSolid, worldMaterial, "worldLogical", self.g4registry)

    def MakeFlukaInitialGeometry(self, worldsize = [5000, 5000, 5000], worldmaterial = "AIR"):
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

    def MakeFlukaBeamPipe(self, name, element,
                          rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                          translation = _np.array([0,0,0]),
                          outer=None,
                          geant4RegistryAdd = False,
                          flukaConvert = True):

        length = element.length*1000
        try :
            g4material = element['beampipeMaterial']
        except :
            g4material = "Temp"

        try :
            beampipeRadius = element['beampipeRadius']
        except :
            beampipeRadius = 30

        try :
            beampipeThickness = element['beampipeThickness']
        except :
            beampipeThickness = 5

        try :
            e1 = element['e1']
        except :
            e1 = 0.0

        try :
            e2 = element['e2']
        except :
            e2 = 0.0

        if geant4RegistryAdd :
            g4registry = self.g4registry
        else :
            g4registry = _pyg4.geant4.Registry()

        # make tubs of correct size
        bpoutersolid    = _pyg4.geant4.solid.Tubs(name+"_outer_solid",
                                                  0,beampipeRadius+beampipeThickness+self.lengthsafety,length,
                                                  0, _np.pi*2, self.g4registry)
        bpouterlogical  = _pyg4.geant4.LogicalVolume(bpoutersolid,g4material,name+"_outer_lv",self.g4registry)
        bpouterphysical = _pyg4.geant4.PhysicalVolume([0,0,0],[0,0,0],bpouterlogical,name+"_outer_pv",None)

        # make actual beampipe
        bpsolid = _pyg4.geant4.solid.CutTubs(name+"_bp_solid",
                                             beampipeRadius, beampipeRadius+beampipeThickness, length,
                                             0, _np.pi*2, [0,0,-1],[0,0,1],self.g4registry)
        bplogical  = _pyg4.geant4.LogicalVolume(bpsolid,g4material,name+"_bp_lv",self.g4registry)
        bpphysical  = _pyg4.geant4.PhysicalVolume([0,0,0],[0,0,0],bplogical,name+"_bp_pv",bpouterlogical,self.g4registry)

        # convert materials
        materialNameSet = bpouterlogical.makeMaterialNameSet()
        self._MakeFlukaMaterials(list(materialNameSet))

        # convert geometry
        if flukaConvert :
            flukaouterregion, self.flukanamecount = _geant4PhysicalVolume2Fluka(bpouterphysical,
                                                                                mtra=rotation,
                                                                                tra=translation,
                                                                                flukaRegistry=self.flukaregistry,
                                                                                flukaNameCount=self.flukanamecount,
                                                                                bakeTransforms=self.bakeTransforms)

        outer = _copy.deepcopy(outer)

        # cut volume out of mother zone
        for daughterzones in flukaouterregion.zones:
            if outer:
                outer.addSubtraction(daughterzones)
            else:
                self.worldzone.addSubtraction(daughterzones)

        # make book keeping information
        self.elementBookkeeping[name] = {}
        self.elementBookkeeping[name]['category'] = 'drift'
        self.elementBookkeeping[name]['physicalVolumes'] = [name+"_outer_pv", name+"_bp_pv", name+"_vac_pv"]
        self.elementBookkeeping[name]['flukaRegions'] = [ self.flukaregistry.PhysVolToRegionMap[pv] for pv in self.elementBookkeeping[name]['physicalVolumes']]
        self.elementBookkeeping[name]['rotation'] = rotation.tolist()
        self.elementBookkeeping[name]['translation'] = translation.tolist()

    def MakeFlukaBeamPipe1(self, name, element,
                          rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                          translation = _np.array([0,0,0]),
                          geant4RegistryAdd = False,
                          flukaConvert = True):

        length = element.length*1000
        try :
            g4material = element['beampipeMaterial']
        except :
            g4material = "Temp"

        try :
            beampipeRadius = element['beampipeRadius']
        except :
            beampipeRadius = 30

        try :
            beampipeThickness = element['beampipeThickness']
        except :
            beampipeThickness = 5

        try :
            e1 = element['e1']
        except :
            e1 = 0.0

        try :
            e2 = element['e2']
        except :
            e2 = 0.0

        if geant4RegistryAdd :
            g4registry = self.g4registry
        else :
            g4registry = _pyg4.geant4.Registry()

        # make tubs of outer size
        bpoutersolid    = self._MakeGeant4GenericTrap(name,length, 100, 100, -e1, e2, g4registry)
        bpouterlogical  = _pyg4.geant4.LogicalVolume(bpoutersolid,"G4_AIR",name+"_outer_lv",g4registry)
        bpouterphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(_tbxyz2matrix([0,-_np.pi/2,0]) @ rotation)),
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
        bplogical  = _pyg4.geant4.LogicalVolume(bpsolid,g4material,name+"_bp_lv",g4registry)
        bpphysical  = _pyg4.geant4.PhysicalVolume([0,_np.pi/2,-_np.pi/2],[0,0,0],bplogical,name+"_bp_pv",bpouterlogical,g4registry)

        vacsolid = _pyg4.geant4.solid.CutTubs(name+"_vac_solid",
                                             0, beampipeRadius, length,
                                             0, _np.pi*2,
                                             _tbxyz2matrix([0,e1,0]) @ _np.array([0,0,-1]),
                                             _tbxyz2matrix([0,-e2,0]) @ _np.array([0,0,1]),
                                             self.g4registry)
        vaclogical  = _pyg4.geant4.LogicalVolume(vacsolid,"G4_Galactic",name+"_cav_lv",g4registry)
        vacphysical  = _pyg4.geant4.PhysicalVolume([0,_np.pi/2,-_np.pi/2],[0,0,0],vaclogical,name+"_vac_pv",bpouterlogical,g4registry)

        # convert materials
        materialNameSet = bpouterlogical.makeMaterialNameSet()
        self._MakeFlukaMaterials(list(materialNameSet))

        # convert geometry
        rotation = rotation @ _tbxyz2matrix([0, 0, -_np.pi / 2]) @ _tbxyz2matrix([0, _np.pi / 2, 0])
        if flukaConvert :
            flukaouterregion, self.flukanamecount = _geant4PhysicalVolume2Fluka(bpouterphysical,
                                                                                mtra=rotation,
                                                                                tra=translation,
                                                                                flukaRegistry=self.flukaregistry,
                                                                                flukaNameCount=self.flukanamecount,
                                                                                bakeTransforms=self.bakeTransforms)


        # cut volume out of mother zone
        for daughterzones in flukaouterregion.zones:
                self.worldzone.addSubtraction(daughterzones)

        # make book keeping information
        self.elementBookkeeping[name] = {}
        self.elementBookkeeping[name]['category'] = 'drift'
        self.elementBookkeeping[name]['physicalVolumes'] = [name+"_outer_pv", name+"_bp_pv", name+"_vac_pv"]
        self.elementBookkeeping[name]['flukaRegions'] = [ self.flukaregistry.PhysVolToRegionMap[pv] for pv in self.elementBookkeeping[name]['physicalVolumes']]
        self.elementBookkeeping[name]['rotation'] = rotation.tolist()
        self.elementBookkeeping[name]['translation'] = translation.tolist()

        # make transformed mesh for overlaps

    def MakeFlukaRectangularStraightOuter(self, straight_x_size, straight_y_size, length, bp_outer_radius = 1, bp_inner_radius = 2, bp_material = "AIR", transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaCircularStraightOuter(self, straight_radius, length, bpOuterRadius = 1, bp_inner_radius = 2, bp_material = "AIR", transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaBendOuter(self, bendXSize, bendYSize, length, angle, bp_outer_radius = 1, bp_inner_radius = 2, bp_material = "AIR", transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaRBend(self, name, element,
                       rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                       translation = _np.array([0,0,0]),
                       geant4RegistryAdd = False,
                       flukaConvert = True) :

        length = element.length*1000

        try :
            angle = element['angle']
        except KeyError :
            print("SBend must have an angle, setting 0")
            angle = 0.0

        g4material = "G4_AIR"

        if geant4RegistryAdd :
            g4registry = self.g4registry
        else :
            g4registry = _pyg4.geant4.Registry()

        # make tubs of correct size
        outersolid    = _pyg4.geant4.solid.Box(name+"_outer_solid",500,500, length, g4registry)
        outerlogical  = _pyg4.geant4.LogicalVolume(outersolid,g4material,name+"_outer_lv",g4registry)
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz( _np.linalg.inv(rotation)),
                                                    translation,
                                                    outerlogical,name+"_outer_pv",
                                                    self.worldLogical,
                                                    g4registry)

        # convert materials
        materialNameSet = outerlogical.makeMaterialNameSet()
        self._MakeFlukaMaterials(list(materialNameSet))

        # convert geometry
        if flukaConvert :
            flukaouterregion, self.flukanamecount = _geant4PhysicalVolume2Fluka(outerphysical,
                                                                                mtra=rotation,
                                                                                tra=translation,
                                                                                flukaRegistry=self.flukaregistry,
                                                                                flukaNameCount=self.flukanamecount,
                                                                                bakeTransforms=self.bakeTransforms)

        # cut volume out of mother zone
        for daughterzones in flukaouterregion.zones:
            self.worldzone.addSubtraction(daughterzones)

        # make beam pipe
        #element.length = 0.90*element.length
        #self.MakeFlukaBeamPipe(name+"_bp", element, rotation=rotation, translation=translation, outer=flukaouterregion)

        # make book keeping information
        self.elementBookkeeping[name] = {}
        self.elementBookkeeping[name]['category'] = 'rbend'
        self.elementBookkeeping[name]['physicalVolumes'] = [name+"_outer_pv"]
        self.elementBookkeeping[name]['flukaRegions'] = [ self.flukaregistry.PhysVolToRegionMap[pv] for pv in self.elementBookkeeping[name]['physicalVolumes']]
        self.elementBookkeeping[name]['rotation'] = rotation.tolist()
        self.elementBookkeeping[name]['translation'] = translation.tolist()

    def MakeFlukaSBend(self, name, element,
                       rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                       translation = _np.array([0,0,0]),
                       geant4RegistryAdd = False,
                       flukaConvert = True):

        length = element.length*1000

        try :
            angle = element['angle']
        except KeyError :
            print("SBend must have an angle, setting 0")
            angle = 0.0

        g4material = "G4_AIR"

        if geant4RegistryAdd :
            g4registry = self.g4registry
        else :
            g4registry = _pyg4.geant4.Registry()

        dz = 2*length/angle*_np.sin(angle/2)

        # make tubs of correct size
        outersolid    = self._MakeGeant4GenericTrap(name,dz, 100, 100, -angle/2, angle/2, g4registry)
        outerlogical  = _pyg4.geant4.LogicalVolume(outersolid,g4material,name+"_outer_lv",g4registry)
        outerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_tbxyz2matrix([_np.pi/2,0,0]) @ _np.linalg.inv(_tbxyz2matrix([0,-_np.pi/2,0]) @ rotation)),
                                                    translation,
                                                    outerlogical,name+"_outer_pv",
                                                    self.worldLogical,
                                                    g4registry)

        # convert materials
        materialNameSet = outerlogical.makeMaterialNameSet()
        self._MakeFlukaMaterials(list(materialNameSet))

        rotation = rotation @ _tbxyz2matrix([0,0,-_np.pi/2]) @ _tbxyz2matrix([0,_np.pi/2,0])
        if flukaConvert :
            flukaouterregion, self.flukanamecount = _geant4PhysicalVolume2Fluka(outerphysical,
                                                                                mtra=rotation,
                                                                                tra=translation,
                                                                                flukaRegistry=self.flukaregistry,
                                                                                flukaNameCount=self.flukanamecount,
                                                                                bakeTransforms=self.bakeTransforms)

        # cut volume out of mother zone
        for daughterzones in flukaouterregion.zones:
            self.worldzone.addSubtraction(daughterzones)

        # make book keeping information
        self.elementBookkeeping[name] = {}
        self.elementBookkeeping[name]['category'] = 'sbend'
        self.elementBookkeeping[name]['physicalVolumes'] = [name+"_outer_pv"]
        self.elementBookkeeping[name]['flukaRegions'] = [ self.flukaregistry.PhysVolToRegionMap[pv] for pv in self.elementBookkeeping[name]['physicalVolumes']]
        self.elementBookkeeping[name]['rotation'] = rotation.tolist()
        self.elementBookkeeping[name]['translation'] = translation.tolist()

    def MakeFlukaQuad(self):
        pass

    def MakeFlukaGeometryPlacement(self, geometry, transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaSplit(self, length, angles = [], bp_outer_radii = [], bp_inner_radii = []):
        pass

    def MakeFlukaSampler(self, name, element,
                         rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                         translation = _np.array([0,0,0]),
                         geant4RegistryAdd = False,
                         flukaConvert = True):

        # parse input key words
        try :
            samplerDiameter = element['samplerDiameter']
        except KeyError:
            samplerDiameter = 1000

        samplerLength = element.length*1000

        try :
            samplerMaterial = element['samplerMaterial']
        except KeyError:
            samplerMaterial = "G4_AIR"

        if geant4RegistryAdd :
            g4registry = self.g4registry
        else :
            g4registry = _pyg4.geant4.Registry()

        # make box of correct size
        samplersolid    = _pyg4.geant4.solid.Box(name+"_solid",samplerDiameter,samplerDiameter,samplerLength,g4registry)
        samplerlogical  = _pyg4.geant4.LogicalVolume(samplersolid,samplerMaterial,name+"_lv",g4registry)
        samplerphysical = _pyg4.geant4.PhysicalVolume(_matrix2tbxyz(_np.linalg.inv(rotation)),
                                                      translation,
                                                      samplerlogical,
                                                      name+"_pv",
                                                      self.worldLogical,
                                                      g4registry)

        # convert materials
        materialNameSet = samplerlogical.makeMaterialNameSet()
        self._MakeFlukaMaterials(list(materialNameSet))

        # convert geometry
        if flukaConvert :
            flukaouterregion, self.flukanamecount = _geant4PhysicalVolume2Fluka(samplerphysical,
                                                                                mtra=rotation,
                                                                                tra=translation,
                                                                                flukaRegistry=self.flukaregistry,
                                                                                flukaNameCount=self.flukanamecount,
                                                                                bakeTransforms=self.bakeTransforms)

        # cut volume out of mother zone
        for daughterzones in flukaouterregion.zones:
            self.worldzone.addSubtraction(daughterzones)

        # make book keeping information
        self.elementBookkeeping[name] = {}
        self.elementBookkeeping[name]['category'] = 'sampler'
        self.elementBookkeeping[name]['physicalVolumes'] = [name+"_pv"]
        self.elementBookkeeping[name]['flukaRegions'] = [ self.flukaregistry.PhysVolToRegionMap[pv] for pv in self.elementBookkeeping[name]['physicalVolumes']]
        self.elementBookkeeping[name]['rotation'] = rotation.tolist()
        self.elementBookkeeping[name]['translation'] = translation.tolist()

        return flukaouterregion.name

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

    def _MakeFlukaMaterials(self, materials = []):
        for g4material in materials :
            if g4material not in self.flukaregistry.materialShortName :
                if type(g4material) is str :
                    g4material = _pyg4.geant4.nist_material_2geant4Material(g4material)
                materialNameShort = "M" + format(self.flukaregistry.iMaterials, "03")
                _geant4Material2Fluka(g4material,self.flukaregistry,materialNameShort=materialNameShort)
                self.flukaregistry.materialShortName[g4material.name] = materialNameShort
                self.flukaregistry.iMaterials += 1

    def ViewGeant4(self):
        v = _pyg4.visualisation.VtkViewerNew()
        v.addLogicalVolume(self.worldLogical)
        v.buildPipelinesAppend()
        v.addAxes(2500)
        v.view()