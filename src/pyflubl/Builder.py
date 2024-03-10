try: # Deprecated, removed in Python 3.10
    from collections import MutableMapping as _MutableMapping
except ImportError: # Python 3.10 onwards.
    from collections.abc import MutableMapping as _MutableMapping
import numbers as _numbers

import numpy as _np
import json as _json

import pyg4ometry as _pyg4
from pyg4ometry.fluka.directive import rotoTranslationFromTra2 as _rotoTranslationFromTra2
from pyg4ometry.convert.geant42Fluka import geant4PhysicalVolume2Fluka as _geant4PhysicalVolume2Fluka
from pyg4ometry.convert.geant42Fluka import geant4Material2Fluka as _geant4Material2Fluka
from pyg4ometry.transformation import matrix2tbxyz as _matrix2tbxyz


pyflublcategories = [
    'drift',
    'rbend',
    'sbend',
    'quadrupole',
    'sampler_plane'
    ]


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
            self._store[key] = '"{}"'.format(value)

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
    def __init__(self):
        self.elements = {}
        self.sequence = []
        self.lenint    = [] # array of length upto a sequence element
        self.transformendint = [] # end point transform
        self.transformmidint = [] # mid point transform
        self.length = 0
        self.maxx = 0.0
        self.maxy = 0.0
        self.maxz = 0.0

        self.lengthsafety = 1e-3
        self.g4registry = _pyg4.geant4.Registry()
        self.flukaregistry = _pyg4.fluka.FlukaRegistry()
        self.flukanamecount = 0

        # persistent book keeping
        self.nameRegion = {}
        self.regionnumber_regionname = {}
        self.regionname_regionnumber = {}
        self.volume_regionname = {}
        self.regionname_volume = {}
        self.samplerinfo = {}

        self.verbose = True

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

            transformmid = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,item.length/2],[0,0,0,1]])
            transformend = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,item.length],[0,0,0,1]])
            if len(self.transformmidint) == 0 :
                self.transformmidint.append(transformmid)
                self.transformendint.append(transformend)
            else :
                self.transformmidint.append(_np.dot(transformmid,self.transformendint[-1]))
                self.transformendint.append(_np.dot(transformend,self.transformendint[-1]))

    def AddElement(self, item):

        if item is not Element :
            msg = "Only Elements or Lines can be added to the machine"
            raise TypeError(msg)

        self.Append(item)
    def AddSplit(self):
        pass

    def AddJoin(self):
        pass

    def AddDrift(self,name, length):
        e = Element(name=name, length=length, category="drift")
        self.Append(e)

    def AddRBend(self, name, length, angle=None, **kwargs):
        e = Element(name=name, length=length, category="rbend", angle=angle)
        self.Append(e)

    def AddSBend(self, name, length, angle=None, **kwargs):
        e = Element(name=name, length = length, category="sbend", angle=angle)
        self.Append(e)

    def AddQuadrupole(self):
        pass

    def AddScoringHistogram(self):
        pass
    def AddScoringMesh(self):
        pass
    def AddSamplerPlane(self, name, length, samplersize):
        e = Element(name=name, length = length, category="sampler_plane", samplersize=samplersize)
        self.Append(e)

    def _MakeBookkeepingInfo(self):

        self.finished = True
        # region number to name
        for i, r in enumerate(self.flukaregistry.regionDict) :

            self.regionnumber_regionname[i+1] = self.flukaregistry.regionDict[r].name
            self.regionname_regionnumber[self.flukaregistry.regionDict[r].name] = i+1

            self.volume_regionname[self.flukaregistry.regionDict[r].comment] = self.flukaregistry.regionDict[r].name
            self.regionname_volume[self.flukaregistry.regionDict[r].name] = self.flukaregistry.regionDict[r].comment


    def _WriteBookkeepingInfo(self, fileName="output.json"):

        if not self.finished :
            self._makeBookkeepingInfo()

        jsonDumpDict = {}
        jsonDumpDict["regionname_regionnumber"] = self.regionname_regionnumber
        jsonDumpDict["regionnumber_regionname"] = self.regionnumber_regionname
        jsonDumpDict["samplerInfo"]            = self.samplerinfo

        with open(fileName, "w") as f:
            _json.dump(jsonDumpDict,f)

    def Write(self, filename):

        freg = self.MakeFlukaModel()

        flukaINPFileName = filename+".inp"
        bookkeepignFileName = filename+".json"

        w = _pyg4.fluka.Writer()
        w.addDetector(self.flukaregistry)
        w.write(flukaINPFileName)

        self._WriteBookkeepingInfo(bookkeepignFileName)
    def MakeFlukaModel(self):

        # make world region and surrounding black body
        self.MakeFlukaInitialGeometry()

        # loop over elements in sequence
        for s,t in zip(self.sequence,self.transformmidint) :
            e = self.elements[s]
            if e.category == "drift" :
                print("making drift")
                self.MakeFlukaBeamPipe(name=e.name, length=e.length*1000, bp_outer_radius=50, bp_inner_radius=40, transform=t)
            elif e.category == "sampler_plane" :
                print("making sampler plane")
                self.MakeFlukaSampler(name=e.name, samplerlength=e.length*1000, samplersize=e['samplersize']*1000, transform=t)

        # make book keeping info
        self._MakeBookkeepingInfo()

    def MakeFlukaInitialGeometry(self, worldsize = [500, 500, 500], worldmaterial = "AIR"):
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

    def MakeFlukaBeamPipe(self, name, length, bp_outer_radius, bp_inner_radius, g4material = "G4_AIR", transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        # translation and rotation
        rot = transform[0:3,0:3]
        dis = transform[0:3,3]*1000

        # get material (TODO fix this complex code)
        if type(g4material) is str :
            g4material = _pyg4.geant4.nist_material_2geant4Material(g4material)
        materialNameShort = "M" + format(self.flukaregistry.iMaterials, "03")
        _geant4Material2Fluka(g4material,self.flukaregistry,materialNameShort=materialNameShort)
        self.flukaregistry.materialShortName[g4material.name] = materialNameShort
        self.flukaregistry.iMaterials += 1

        # make tubs of correct size
        bpoutersolid    = _pyg4.geant4.solid.Tubs(name+"_outer_solid",0,bp_outer_radius+self.lengthsafety,length,0, _np.pi*2, self.g4registry)
        bpouterlogical  = _pyg4.geant4.LogicalVolume(bpoutersolid,g4material,name+"_outer_lv",self.g4registry)
        bpouterphysical = _pyg4.geant4.PhysicalVolume([0,0,0],[0,0,0],bpouterlogical,name+"_outer_pv",None)

        # make actual beampipe
        bpsolid = _pyg4.geant4.solid.CutTubs(name+"_bp_solid",bp_inner_radius, bp_outer_radius, length, 0, _np.pi*2, [0,0,-1],[0,0,1],self.g4registry)
        bplogical  = _pyg4.geant4.LogicalVolume(bpsolid,g4material,name+"_bp_lv",self.g4registry)
        bpphysical  = _pyg4.geant4.PhysicalVolume([0,0,0],[0,0,0],bplogical,name+"_bp_pv",bpouterlogical,self.g4registry)

        flukaouterregion, self.flukanamecount = _geant4PhysicalVolume2Fluka(bpouterphysical,
                                                                            mtra=rot,
                                                                            tra=dis,
                                                                            flukaRegistry=self.flukaregistry,
                                                                            flukaNameCount=self.flukanamecount)

        # cut volume out of mother zone
        for daughterzones in flukaouterregion.zones:
            self.worldzone.addSubtraction(daughterzones)

    def MakeFlukaRectangularStraightOuter(self, straight_x_size, straight_y_size, length, bp_outer_radius = 1, bp_inner_radius = 2, bp_material = "AIR", transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaCircularStraightOuter(self, straight_radius, length, bpOuterRadius = 1, bp_inner_radius = 2, bp_material = "AIR", transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaBendOuter(self, bendXSize, bendYSize, length, angle, bp_outer_radius = 1, bp_inner_radius = 2, bp_material = "AIR", transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaSBend(self, length, angle,
                       bendxsize, bendysize, bpouterradius, bpinnterradius,
                       bpmaterial = "G4_AIR",
                       transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass


    def MakeFlukaQuad(self):
        pass

    def MakeFlukaGeometryPlacement(self, geometry, transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
        pass

    def MakeFlukaSplit(self, length, angles = [], bp_outer_radii = [], bp_inner_radii = []):
        pass

    def MakeFlukaSampler(self, name = "sampler", samplersize = 1e3, samplerlength=1, transform = _np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]),
                         g4material="G4_AIR", fmaterial = None):

        # translation and rotation
        rot = transform[0:3,0:3]
        dis = transform[0:3,3]*1000

        # get material (TODO fix this complex code)
        if type(g4material) is str :
            g4material = _pyg4.geant4.nist_material_2geant4Material(g4material)
        materialNameShort = "M" + format(self.flukaregistry.iMaterials, "03")
        _geant4Material2Fluka(g4material,self.flukaregistry,materialNameShort=materialNameShort)
        self.flukaregistry.materialShortName[g4material.name] = materialNameShort
        self.flukaregistry.iMaterials += 1

        # make box of correct size
        samplersolid    = _pyg4.geant4.solid.Box(name+"_solid",samplersize,samplersize,samplerlength,self.g4registry)
        samplerlogical  = _pyg4.geant4.LogicalVolume(samplersolid,g4material,name+"_lv",self.g4registry)
        samplerphysical = _pyg4.geant4.PhysicalVolume([0,0,0],[0,0,0],samplerlogical,name+"_pv",None)

        flukaouterregion, self.flukanamecount = _geant4PhysicalVolume2Fluka(samplerphysical,
                                                                            mtra=rot,
                                                                            tra=dis,
                                                                            flukaRegistry=self.flukaregistry,
                                                                            flukaNameCount=self.flukanamecount)

        # cut volume out of mother zone
        for daughterzones in flukaouterregion.zones:
            self.worldzone.addSubtraction(daughterzones)

        self.samplerinfo[name] = {"name":name, "type":"plane","regionName":flukaouterregion.name}

        return flukaouterregion.name