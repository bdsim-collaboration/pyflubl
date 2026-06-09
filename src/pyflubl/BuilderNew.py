from collections import defaultdict as _defaultdict
import numpy as _np
import json as _json
import pprint as _pprint
import copy as _copy

from .Coordinates import Coordinates as _Coordinates
from .Options import Options as _Options
from .Element import Element as _Element
from .Element import ElementGap as _ElementGap
from .Element import ElementCustomG4 as _ElementCustomG4
from .Element import ElementCustomFluka as _ElementCustomFluka
from .GeometryGeant4 import PlacementType as _PlacementType
from .GeometryGeant4 import MakeOuterTrapezoid as _MakeOuterTrapezoid
from .GeometryGeant4 import MakeBeamPipeCircular as _MakeBeamPipeCircular
from .GeometryGeant4 import MakeTarget as _MakeTarget
from .GeometryGeant4 import MakeRCol as _MakeRCol
from .GeometryGeant4 import MakeECol as _MakeECol
from .GeometryGeant4 import MakeJCol as _MakeJCol
from .GeometryGeant4 import MakeShield as _MakeShield
from .GeometryGeant4 import MakeDump as _MakeDump
from .GeometryGeant4 import MakeWireScanner as _MakeWireScanner

import pyg4ometry as _pyg4
from pyg4ometry.fluka.directive import rotoTranslationFromTra2 as _rotoTranslationFromTra2
from pyg4ometry.convert.geant42Fluka import geant4PhysicalVolume2Fluka as _geant4PhysicalVolume2Fluka
from pyg4ometry.transformation import matrix2tbxyz as _matrix2tbxyz
from pyg4ometry.transformation import tbxyz2matrix as _tbxyz2matrix
from pyg4ometry.transformation import tbxyz2axisangle as _tbxyz2axisangle

from .Fluka import Lattice  as _Lattice
from .Fluka import Mgnfield as _Mgnfield
from .Fluka import Mgncreat as _Mgncreat
from .Fluka import Stepsize as _Stepsize
from .Fluka import Rotprbin as _Rotprbin

class Machine(_Coordinates) :
    """Build and export beamline models to Geant4 and FLUKA representations."""
    def __init__(self, bakeTransforms = True, verbose = False) :
        """Initialise a machine builder with geometry, bookkeeping, and control-card state."""
        super().__init__()

        # store if transforms are baked into bodies or rotdefis used
        self.bakeTransforms = bakeTransforms

        # verbose debugging information
        self.verbose = verbose

        # finished creation
        self.finished = False

        # element prototypes
        self.prototypes = {}

        # options (a.k.a defaults)
        self.options = _Options()

        # total length of machine
        self.length = 0

        # extent of machine
        self.world_min = [ 0, 0, 0]
        self.world_max = [ 0, 0, 0]

        # extent of prototypes
        self.prototype_min = [ 0, 0, 0]
        self.prototype_max = [ 0, 0, 0]

        # extent of simulation (max and min of machine and prototypes)
        self.simulation_min = [ 0, 0, 0]
        self.simulation_max = [ 0, 0, 0]

        # offset between prototypes and world
        self.prototype_world_offset = [ 0, 0, 0]

        # current prototype location
        self.prototype_position = [ 0, 0, 0]
        self.prototype_pad = [ 100, 100, 100]

        # geometry registries (will be populated when MakeFlukaModel is called)
        self.g4registry = None
        self.flukaregistry = None

        # element to book-keeping-dict information
        self.elementBookkeeping = _defaultdict()

        # persistent book keeping
        self.nameRegion = {}
        self.regionnumber_regionname = {}
        self.regionnumber_element = {}
        self.regionname_regionnumber = {}
        self.volume_regionname = {}
        self.regionname_volume = {}
        self.usrbinnumber_usrbininfo = {}
        self.samplernames_samplernumber= {}

        # fluka indices
        self.flukanamecount = 0
        self.flukamgncount = 0     # number of magnetic field ROT-DEF placements
        self.flukabincount = 0
        self.flukalatcount = 0

        # fluka control cards
        self.beam = None
        self.beam1 = None
        self.beampos = None
        self.beamaxes = None
        self.defaults = None
        self.elcfield = None
        self.title = None
        self.fglobal = None
        self.lattice = []
        self.mgnfield = []
        self.mgncreat = []
        self.mgndata = []
        self.stepsize = []
        self.rotprbin = []
        self.randomiz = None
        self.source = None
        self.start = None
        self.usrbin = []
        self.userdump = []
        self.usricall = None
        self.usrocall = None

    def AddDrift(self,name, length, add=True, **kwargs):
        """Add drift configuration to the machine."""
        allowed_keys = _Element._beampipe_allowed_keys + \
                       _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys
        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="drift", length=length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddRBend(self, name, length, add=True, **kwargs):
        """Add rbend configuration to the machine."""
        allowed_keys = _Element._beampipe_allowed_keys + \
                       _Element._outer_allowed_keys + \
                       _Element._rbend_allowed_keys + \
                       _Element._tiltshift_allowed_keys
        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)

        kwargs['outerE1'] = -kwargs['e1']
        kwargs['outerE2'] = -kwargs['e2']

        e = _Element(name=name, category="rbend", length=length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddSBend(self, name, length, add=True, **kwargs):
        """Add sbend configuration to the machine."""
        allowed_keys = _Element._beampipe_allowed_keys + \
                       _Element._outer_allowed_keys + \
                       _Element._sbend_allowed_keys + \
                       _Element._tiltshift_allowed_keys

        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)

        # need to set the outer trap angles for Sbend
        kwargs['outerE1'] = -kwargs['angle']/2 - kwargs['e1']
        kwargs['outerE2'] = -kwargs['angle']/2 - kwargs['e2']

        e = _Element(name=name, category="sbend", length = length, **kwargs)
        if add :
            self.Append(e)

        return e

    def AddSBendSplit(self, name, length, nsplit=10, add=True, **kwargs):
        """Add sbend split configuration to the machine."""
        angle = kwargs.pop('angle')/nsplit
        length = length/nsplit

        sbends = []
        for i in range(0,nsplit):
            s = self.AddSBend(name+"_split_"+str(i), length, angle = angle, add=add, **kwargs)
            sbends.append(s)
        return sbends

    def AddQuadrupole(self, name, length, add=True, **kwargs):
        """Add quadrupole configuration to the machine."""
        allowed_keys = _Element._beampipe_allowed_keys + \
                       _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._quadrupole_allowed_keys

        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="quadrupole", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddSextupole(self, name, length, add = True, **kwargs):
        """Add sextupole configuration to the machine."""
        allowed_keys = _Element._beampipe_allowed_keys + \
                       _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._sextupole_allowed_keys

        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="sextupole", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddOctupole(self, name, length, add = True, **kwargs):
        """Add octupole configuration to the machine."""
        allowed_keys = _Element._beampipe_allowed_keys + \
                       _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._octupole_allowed_keys

        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="octupole", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddDecapole(self, name, length, add = True, **kwargs):
        """Add decapole configuration to the machine."""
        allowed_keys = _Element._beampipe_allowed_keys + \
                       _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._decapole_allowed_keys

        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="decapole", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddTarget(self, name, length, add=True, **kwargs):
        """Add target configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._target_allowed_keys

        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="target", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddRCol(self, name, length, add=True, **kwargs):
        """Add rcol configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._rcol_allowed_keys
        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="rcol", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddECol(self, name, length, add=True, **kwargs):
        """Add ecol configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._ecol_allowed_keys
        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="ecol", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddJCol(self, name, length, add=True, **kwargs):
        """Add jcol configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._jcol_allowed_keys
        self._CheckElementKwargs(kwargs,allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="jcol", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddShield(self, name, length, add=True, **kwargs):
        """Add shield configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._beampipe_allowed_keys + \
                       _Element._shield_allowed_keys
        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="shield", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddDump(self, name, length, add=True, **kwargs):
        """Add dump configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._target_allowed_keys

        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="dump", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddWireScanner(self, name, length, add=True, **kwargs):
        """Add wire scanner configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys + \
                       _Element._beampipe_allowed_keys + \
                       _Element._wirescanner_allowed_keys

        self._CheckElementKwargs(kwargs,allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="wirescanner", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddGap(self, name, length, add=True, **kwargs):
        """Add gap configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._tiltshift_allowed_keys
        self._CheckElementKwargs(kwargs,allowed_keys)
        self._SetDefaultElementKwargs(kwargs,allowed_keys)
        e = _Element(name, category="gap", length = length, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddCustomG4(self, name, length, containerLV, add=True, **kwargs):
        """Add custom g4 configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._customg4_allowed_keys + \
                       _Element._customg4file_allowed_keys + \
                       _Element._tiltshift_allowed_keys
        self._CheckElementKwargs(kwargs,allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)
        e = _Element(name=name, category="customG4", length = length, containerLV=containerLV, **kwargs)
        #e = _ElementCustomG4(name, length, containerLV, **kwargs)
        if add :
            self.Append(e)
        return e

    def AddCustomG4File(self, name, length, add=True, **kwargs):
        """Add custom g4 file configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._customg4file_allowed_keys + \
                       _Element._tiltshift_allowed_keys
        self._CheckElementKwargs(kwargs,allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)

        geometry_file = kwargs['geometryFile']
        lv_name = kwargs['lvName']

        # registry for converter
        g4registry = self._GetGeant4Registry(True)

        # load file
        reader = _pyg4.gdml.Reader(geometry_file, registryIn = g4registry)
        lv = g4registry.logicalVolumeDict[lv_name]

        return self.AddCustomG4(name,length, containerLV = lv, add=add, **kwargs)

    def AddCustomFluka(self, name, length, add=True, **kwargs):
        """Add custom fluka configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys +\
                       _Element._customfluka_allowed_keys + \
                       _Element._customflukafile_allowed_keys + \
                       _Element._tiltshift_allowed_keys
        self._CheckElementKwargs(kwargs,allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)

        e = _Element(name=name,
                     category="customFluka",
                     length=length,
                     **kwargs)
        if add :
            self.Append(e)
        return e

    def AddCustomFlukaFile(self, name, length, add=True, **kwargs):
        """Add custom fluka file configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._customflukafile_allowed_keys + \
                       _Element._tiltshift_allowed_keys
        self._CheckElementKwargs(kwargs,allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)

        geometry_file = kwargs['geometryFile']
        outer_region = kwargs['customOuterRegion']
        outer_bodies = kwargs['customOuterBodies']
        regions = kwargs['customRegions']

        reader = _pyg4.fluka.Reader(geometry_file)
        registry = reader.getRegistry()

        i_body_rename = 0
        i_region_rename = 0

        # rename bodies
        outer_bodies_rename = []
        regions_rename = []

        # rename bodies
        for k in list(registry.bodyDict.keys()):
            new_name = name.upper()+format(i_body_rename, "03")
            if k in outer_bodies :
                outer_bodies_rename.append(new_name)
            registry.bodyDict[k].name = new_name
            registry.bodyDict[new_name] = registry.bodyDict.pop(k)
            i_body_rename += 1
        outer_bodies = outer_bodies_rename

        # rename regions
        for k in list(registry.regionDict.keys()):
            new_name = name.upper()+format(i_region_rename, "03")
            if k in regions :
                regions_rename.append(new_name)
            if k == outer_region :
                outer_region = new_name
            registry.regionDict[k].name = new_name
            registry.regionDict[new_name] = registry.regionDict.pop(k)
            i_region_rename += 1

            # fix the assignmas too
            assignma = list(registry.assignmas.pop(k))
            registry.assignmas[new_name] = assignma

        regions = regions_rename

        if isinstance(outer_bodies, str) :
            outer_bodies = [registry.bodyDict[k] for k in outer_bodies.split()]
        elif isinstance(outer_bodies, list) :
            outer_bodies = [registry.bodyDict[k] for k in outer_bodies]

        if isinstance(regions, str) :
            regions = [registry.regionDict[k] for k in regions.split()]
        elif isinstance(regions, list) :
            regions = [registry.regionDict[k] for k in regions]

        outer_region = registry.regionDict[outer_region]

        kwargs['geometryFile'] = geometry_file
        kwargs['customOuterRegion'] = outer_region
        kwargs['customOuterBodies'] = outer_bodies
        kwargs['customRegions'] = regions

        return self.AddCustomFluka(name,
                                   length,
                                   flukaRegistry=registry,
                                   add=add,
                                   **kwargs)

    def AddLatticeInstance(self, name, prototypeName, **kwargs):

        """Add lattice instance configuration to the machine."""
        allowed_keys = _Element._tiltshift_allowed_keys
        self._CheckElementKwargs(kwargs,allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)

        e = _Element(name=name,
                     category="lattice_instance",
                     length=self.prototypes[prototypeName]['element'].length,
                     prototype = self.prototypes[prototypeName]['element'],
                     **kwargs)
        self.Append(e)
        return e

    def AddLatticePrototype(self, e, **kwargs):
        # save in prototype dict
        # transformation information to be populated when built
        """Add lattice prototype configuration to the machine."""
        self.prototypes[e.name] = {"element":e}

    def AddSamplerPlane(self, name, length = None, **kwargs):
        """Add sampler plane configuration to the machine."""
        allowed_keys = _Element._outer_allowed_keys + \
                       _Element._sampler_plane_allowed_keys + \
                       _Element._tiltshift_allowed_keys
        self._CheckElementKwargs(kwargs, allowed_keys)
        self._SetDefaultElementKwargs(kwargs, allowed_keys)

        # deftault sampler length
        if not length:
            length = self.options.samplerLength

        e = _Element(name=name, category="sampler_plane", length = length, **kwargs)
        self.Append(e)

        # Add bookkeeping information
        self.samplernames_samplernumber[name] = len(self.samplernames_samplernumber)

    def AddScoringHistogram(self):
        """Add scoring histogram configuration to the machine."""
        pass

    def AddScoringMesh(self):
        """Add scoring mesh configuration to the machine."""
        pass

    def _CheckElementKwargs(self, kwargs, allowed_keys):
        """Internal helper for check element kwargs."""
        for key in kwargs:
            if key not in allowed_keys:
                raise TypeError(f"Unexpected keyword argument: {key}")

    def _SetDefaultElementKwargs(self, kwargs, allowed_keys):
        """Internal helper for set default element kwargs."""
        for ak in allowed_keys :
            if ak not in kwargs :
                if ak == "vacuumMaterial" :
                    kwargs[ak] = self.options.vacuumMaterial
                elif ak == "beampipeMaterial" :
                    kwargs[ak] = self.options.beampipeMaterial
                elif ak == "beampipeRadius" :
                    kwargs[ak] = self.options.beampipeRadius
                elif ak == "beampipeThickness" :
                    kwargs[ak] = self.options.beampipeThickness
                elif ak == "outerHorizontalSize" :
                    kwargs[ak] = self.options.outerHorizontalSize
                elif ak == "outerVerticalSize" :
                    kwargs[ak] = self.options.outerVerticalSize
                elif ak == "outerMaterial" :
                    kwargs[ak] = self.options.outerMaterial
                elif ak == "outerE1" :
                    kwargs[ak] = 0.0
                elif ak == "outerE2" :
                    kwargs[ak] = 0.0
                elif ak == "outerP1" :
                    kwargs[ak] = 0.0
                elif ak == "outerP2" :
                    kwargs[ak] = 0.0
                elif ak == "e1" :
                    kwargs[ak] = 0.0
                elif ak == "e2" :
                    kwargs[ak] = 0.0
                elif ak == "offsetX" :
                    kwargs[ak] = 0.0
                elif ak == "offsetY" :
                    kwargs[ak] = 0.0
                elif ak  == "tilt" :
                    kwargs[ak] = 0.0
                elif ak == "xsize" :
                    kwargs[ak] = 0.0
                elif ak == "ysize" :
                    kwargs[ak] = 0.0
                elif ak == "xsizeLeft" :
                    kwargs[ak] = 0.0
                elif ak == "xsizeRight" :
                    kwargs[ak] = 0.0
                elif ak == "horizontalWidth" :
                    kwargs[ak] = self.options.outerHorizontalSize*0.95
                elif ak == "verticalWidth" :
                    kwargs[ak] = self.options.outerVerticalSize*0.95
                elif ak == "material" :
                    kwargs[ak] = "IRON"
                elif ak == "jawTiltLeft" :
                    kwargs[ak] = 0.0
                elif ak == "jawTiltRight" :
                    kwargs[ak] = 0.0
                elif ak == "apertureType" :
                    kwargs[ak] = "circular"
                elif ak == "wireDiameter" :
                    kwargs[ak] = 5
                elif ak == "wireLength" :
                    kwargs[ak] = 25
                elif ak == "wireMaterial" :
                    kwargs[ak] = "IRON"
                elif ak == "wireAngle" :
                    kwargs[ak] = 0.0
                elif ak == "wireOffsetX" :
                    kwargs[ak] = 0.0
                elif ak == "wireOffsetY" :
                    kwargs[ak] = 0.0
                elif ak == "wireOffsetZ" :
                    kwargs[ak] = 0.0
                elif ak == "samplerMaterial" :
                    kwargs[ak] = self.options.samplerMaterial
                elif ak == "samplerLength" :
                    kwargs[ak] = self.options.samplerLength
                elif ak == "samplerDiameter" :
                    kwargs[ak] = self.options.samplerDiameter
                elif ak == "convertMaterials" :
                    kwargs[ak] = True
                else :
                    pass

    def AddBeam(self, beam):
        """Add beam configuration to the machine."""
        self.beam = beam

    def AddBeampos(self, beampos):
        """Add beampos configuration to the machine."""
        self.beampos = beampos

    def AddBeamaxes(self, beamaxes):
        """Add beamaxes configuration to the machine."""
        self.beamaxes = beamaxes

    def AddDefaults(self, defaults):
        """Add defaults configuration to the machine."""
        self.defaults = defaults

    def AddElcfield(self, elcfield):
        """Add elcfield configuration to the machine."""
        self.elcfield = elcfield

    def AddGlobal(self, fglobal):
        """Add global configuration to the machine."""
        self.fglobal = fglobal

    def AddLattice(self, lattice):
        """Add lattice configuration to the machine."""
        self.lattice.append(lattice)

    def AddMgnfield(self, mgnfield):
        """Add mgnfield configuration to the machine."""
        self.mgnfield.append(mgnfield)

    def AddMgncreat(self, mgncreat):
        """Add mgncreat configuration to the machine."""
        self.mgncreat.append(mgncreat)

    def AddMgndata(self, mgndata):
        """Add mgndata configuration to the machine."""
        self.mgndata.append(mgndata)

    def AddStepsize(self, stepsize):
        """Add stepsize configuration to the machine."""
        self.stepsize.append(stepsize)

    def AddRotprbin(self, rotprbin):
        """Add rotprbin configuration to the machine."""
        self.rotprbin.append(rotprbin)

    def AddRandomiz(self, randomiz):
        """Add randomiz configuration to the machine."""
        self.randomiz = randomiz

    def AddSource(self,source):
        """Add source configuration to the machine."""
        self.source = source

    def AddStart(self, start):
        """Add start configuration to the machine."""
        self.start = start

    def AddTitle(self, title):
        """Add title configuration to the machine."""
        self.title = title

    def AddUsrbin(self, usrbin, rotmat = _np.array([[1,0,0],[0,1,0],[0,0,1]]), translation = _np.array([0,0,0])):

        """Add usrbin configuration to the machine."""
        self.usrbin.append(usrbin)

        # Add bookkeeping information
        self._AddBookkeepingUsrbin(self.flukabincount, usrbin.name, rotmat, translation)

        # increment counter for added usrbin
        self.flukabincount += 1

    def AddUsrbinToElement(self, element, usrbin = None, scaleUsrbinToElement = False):

        # build coordinates
        """Add usrbin to element configuration to the machine."""
        self.Build()

        # get element name
        if type(element) is str :
            element_name = element
        else :
            element_name = element.name

        # element index
        element_idx = list(self.elements.keys()).index(element_name)

        # get transformation
        element_rotmat = self.rot_mid[element_idx]
        element_rotmat_inv = _np.linalg.inv(element_rotmat)

        element_rot_inv = _matrix2tbxyz(element_rotmat_inv)
        element_translation = self.arc_mid[element_idx]*1000
        element_translation_inv = - element_rotmat_inv @ element_translation

        # make rotdefi
        transformation_name = "TB"+format(self.flukabincount, "03")
        rdi = _rotoTranslationFromTra2(transformation_name,[element_rot_inv, element_translation_inv])
        if len(rdi) > 0 :
            self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

        # add ROTPRBIN
        rotprbin = _Rotprbin(storagePrecision=0,
                             rotDefi=transformation_name,
                             usrbinStart=usrbin.name)
        self.AddRotprbin(rotprbin)

        # add USRBIN
        self.AddUsrbin(usrbin, element_rotmat, element_translation)

    def AddUserdump(self, userdump):
        """Add userdump configuration to the machine."""
        self.userdump.append(userdump)

    def AddUsricall(self, usricall):
        """Add usricall configuration to the machine."""
        self.usricall = usricall

    def AddUsrocall(self, usrocall):
        """Add usrocall configuration to the machine."""
        self.usrocall = usrocall

    def _MakeBookkeepingInfo(self):
        """Internal helper for make bookkeeping info."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine._MakeBookkeepingInfo: Making bookkeeping information...")

        self.finished = True

        # loop over elements and put S location
        for i, e in enumerate(self.elements):
            self.elementBookkeeping[e]["S"] = self.s_mid[i]
            self.elementBookkeeping[e]["length"] = self.elements[e].length

        # region number to name
        for i, r in enumerate(self.flukaregistry.regionDict) :
            self.regionnumber_regionname[i+1] = self.flukaregistry.regionDict[r].name
            self.regionname_regionnumber[self.flukaregistry.regionDict[r].name] = i+1

            self.volume_regionname[self.flukaregistry.regionDict[r].comment] = self.flukaregistry.regionDict[r].name
            self.regionname_volume[self.flukaregistry.regionDict[r].name] = self.flukaregistry.regionDict[r].comment

            # loop over all elements and find reference to the region in an element
            for element_name, element_info in self.elementBookkeeping.items() :
                if self.flukaregistry.regionDict[r].name in element_info['flukaRegions'] :
                    self.regionnumber_element[i+1] = element_name

    def _WriteBookkeepingInfo(self, fileName="output.json", pretty=False):

        """Internal helper for write bookkeeping info."""
        if not self.finished :
            self._MakeBookkeepingInfo()

        jsonDumpDict = {}
        jsonDumpDict["elements"] = dict(self.elementBookkeeping)
        jsonDumpDict["samplernames_samplernumber"] = self.samplernames_samplernumber
        jsonDumpDict["regionname_regionnumber"] = self.regionname_regionnumber
        jsonDumpDict["regionnumber_regionname"] = self.regionnumber_regionname
        jsonDumpDict["regionnumber_element"] = self.regionnumber_element
        jsonDumpDict["usrbinnumber_usrbininfo"] = self.usrbinnumber_usrbininfo

        if not pretty :
            with open(fileName, "w") as f:
                _json.dump(jsonDumpDict,f)
        else :
            # write json to file with human-friendly formatting
            pretty_json_str = _pprint.pformat(jsonDumpDict, compact=True).replace("'", '"')

            with open(fileName, 'w') as f:
                f.write(pretty_json_str)

    def Write(self, filename, prettyJSON = False):
        """Handle write operations for the machine builder."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.Write: Writing model to file...")

        self.MakeFlukaModel()

        flukaINPFileName = filename+".inp"
        geant4GDMLFileName = filename+".gdml"
        bookkeepignFileName = filename+".json"

        if self.beam :
            self.beam.AddRegistry(self.flukaregistry)
        if self.beam1 :
            self.beam1.AddRegistry(self.flukaregistry)
        if self.beampos :
            self.beampos.AddRegistry(self.flukaregistry)
        if self.beamaxes :
            self.beamaxes.AddRegistry(self.flukaregistry)
        if self.defaults :
            self.defaults.AddRegistry(self.flukaregistry)
        if self.elcfield :
            self.elcfield.AddRegistry(self.flukaregistry)
        if self.fglobal:
            self.fglobal.AddRegistry(self.flukaregistry)
        if len(self.lattice) > 0 :
            for la in self.lattice:
                la.AddRegistry(self.flukaregistry)
        if len(self.mgnfield) > 0 :
            for mf in self.mgnfield:
                mf.AddRegistry(self.flukaregistry)
        if len(self.mgncreat) > 0 :
            for mc in self.mgncreat:
                mc.AddRegistry(self.flukaregistry)
        if len(self.stepsize) > 0 :
            for ss in self.stepsize:
                ss.AddRegistry(self.flukaregistry)
        if len(self.rotprbin) > 0 :
            for pr in self.rotprbin:
                pr.AddRegistry(self.flukaregistry)
        if self.randomiz :
            self.randomiz.AddRegistry(self.flukaregistry)
        if self.source :
            self.source.AddRegistry(self.flukaregistry)
        if self.start :
            self.start.AddRegistry(self.flukaregistry)
        if self.title:
            self.title.AddRegistry(self.flukaregistry)
        if len(self.usrbin) > 0 :
            for ub in self.usrbin:
                ub.AddRegistry(self.flukaregistry)
        if len(self.userdump) > 0 :
            for ud in self.userdump:
                ud.AddRegistry(self.flukaregistry)
        if self.usricall :
            self.usricall.AddRegistry(self.flukaregistry)
        if self.usrocall :
            self.usrocall.AddRegistry(self.flukaregistry)

        fw = _pyg4.fluka.Writer()
        fw.addDetector(self.flukaregistry)
        fw.write(flukaINPFileName)

        gw = _pyg4.gdml.Writer()
        gw.addDetector(self._GetGeant4Registry(geant4RegistryAdd=True))
        gw.write(geant4GDMLFileName)

        self._WriteBookkeepingInfo(bookkeepignFileName, pretty=prettyJSON)

    def __repr__(self):
        """Return a readable summary of the machine configuration."""
        s = ''
        s += 'pyflubl.BuilderNew.Machine instance\n'
        s += str(len(self.sequence)) + ' items in sequence\n'
        s += str(len(self.elements)) + ' unique elements defined\n'
        return s

    def MakeFlukaModel(self):
        """Build fluka model objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaModel:")

        # make registries
        self.flukaregistry = self._GetFlukaRegistry(True)
        self.g4registry    = self._GetGeant4Registry(True)

        # build coordinates
        self.Build(circular=False)

        # initial world size
        extent = self.CalculateExtent()

        # sizes in cm
        xmax = max(abs(extent[0][0]), abs(extent[1][0]))*100
        ymax = max(abs(extent[0][1]), abs(extent[1][1]))*100
        zmax = max(abs(extent[0][2]), abs(extent[1][2]))*100

        # make world region and surrounding black body
        self.MakeFlukaInitialGeometry(world_min=[c*100 for c in extent[0]],
                                      world_max=[c*100 for c in extent[1]],
                                      worldmaterial=self.options.worldMaterial)
        self.MakeGeant4InitialGeometry(worldsize=[2*xmax*10, 2*ymax*10, 2*zmax*10])


        # fix faces of elements
        # self._FixElementFaces(view=False)

        # make lattice prototypes
        for prototype in self.prototypes :
            pass

        # loop over elements in sequence
        # (r)rotation, (t)translation, (g)geom(t)ranslation,
        # (c)ubical(b)ounding,
        # (t)rapezoidal(b)ounding
        for name,r,t,gt,cb, tb in zip(self.sequence,self.rot_mid, self.arc_mid, self.cho_mid, self.cub_loc, self.tra_loc) :
            e = self.elements[name]

            # populate initial book keeping information
            if name not in self.elementBookkeeping:
                self.elementBookkeeping[name] = {}

            # make element
            self.ElementFactory(e, r, t, gt, cb, tb)

        # make book keeping info
        self._MakeBookkeepingInfo()

        return self.flukaregistry

    def MakeGeant4InitialGeometry(self, worldsize = [5000, 5000, 5000], worldMaterial = "G4_AIR"):
        """Build geant4 initial geometry objects for geometry conversion and export."""
        worldSolid = _pyg4.geant4.solid.Box("world",worldsize[0], worldsize[1], worldsize[2], self._GetGeant4Registry(geant4RegistryAdd=True))
        self.worldLogical = _pyg4.geant4.LogicalVolume(worldSolid, worldMaterial, "worldLogical", self._GetGeant4Registry(geant4RegistryAdd=True))
        self._GetGeant4Registry(geant4RegistryAdd=True).setWorldVolume(self.worldLogical)

    def MakeFlukaInitialGeometry(self,
                                 world_min = [-250, -250, -250],
                                 world_max = [ 250,  250,  250],
                                 worldmaterial = "AIR",
                                 world_pad = 200):

        # store world size
        """Build fluka initial geometry objects for geometry conversion and export."""
        self.world_min = world_min
        self.world_max = world_max
        self.simulation_min = world_min
        self.simulation_max = world_max

        # prototype
        if len(self.prototypes) != 0 :
            world_dz = world_max[2] - world_min[2]

            self.prototype_min = [self.world_min[0], self.world_min[1], self.world_min[2] - world_dz]
            self.prototype_max = [self.world_max[0], self.world_max[1], self.world_max[2] - world_dz]

            self.simulation_min = [ min(cw,cp) for cw, cp in zip(self.world_min,self.prototype_min)]
            self.simulation_max = [ max(cw,cp) for cw, cp in zip(self.world_max,self.prototype_max)]

            self.prototype_world_offset = [0,0, world_dz]

            self.prototype_position = [ self.prototype_min[0] + self.prototype_pad[0],
                                        0,
                                        self.prototype_min[2] + self.prototype_pad[2]]

        blackbody = _pyg4.fluka.RPP("BLKBODY",
                               self.simulation_min[0]-world_pad, self.simulation_max[0]+world_pad,
                               self.simulation_min[1]-world_pad, self.simulation_max[1]+world_pad,
                               self.simulation_min[2]-world_pad, self.simulation_max[2]+world_pad,
                               transform=_rotoTranslationFromTra2("BBROTDEF",[[0,0,0],[0,0,0]],
                                                                  flukaregistry=self.flukaregistry),
                               flukaregistry=self.flukaregistry)

        worldbody = _pyg4.fluka.RPP("WORLD",
                               self.simulation_min[0],self.simulation_max[0],
                               self.simulation_min[1],self.simulation_max[1],
                               self.simulation_min[2],self.simulation_max[2],
                               transform=_rotoTranslationFromTra2("BBROTDEF",[[0,0,0],[0,0,0]],
                                                                  flukaregistry=self.flukaregistry),
                               flukaregistry=self.flukaregistry)

        self.blackbodyzone = _pyg4.fluka.Zone()
        self.worldzone     = _pyg4.fluka.Zone()
        self.parkingzone   = _pyg4.fluka.Zone()

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

        # if there are not prototype elements return
        if len(self.prototypes) == 0 :
            return

        parkingbody = _pyg4.fluka.RPP("PRKBODY",
                                      self.prototype_min[0]+1, self.prototype_max[0]-1,
                                      self.prototype_min[1]+1, self.prototype_max[1]-1,
                                      self.prototype_min[2]+1, self.prototype_max[2]-1,
                                      transform=_rotoTranslationFromTra2("PRKROTDEF",[[0,0,0],[0,0,0]],
                                                                         flukaregistry=self.flukaregistry),
                                      flukaregistry=self.flukaregistry)

        self.worldzone.addSubtraction(parkingbody)
        self.parkingzone.addIntersection(parkingbody)
        self.parkingregion = _pyg4.fluka.Region("PARKING")
        self.parkingregion.addZone(self.parkingzone)
        self.flukaregistry.addMaterialAssignments("GOLD","PARKING")
        self.flukaregistry.addRegion(self.parkingregion)

    def ElementFactory(self,
                       element,
                       rotation,
                       translation,
                       geomtranslation,
                       cubicalbound,
                       trapezoidalbound,
                       g4add = True,
                       flukaConvert = True,
                       prototype = False):
        """Handle element factory operations for the machine builder."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.ElementFactory: Making FLUKA geometry for ", element.name, element.category)

        if element.category == "drift":
            return self.MakeFlukaDrift(name=element.name,
                                       element=element,
                                       rotation=rotation,
                                       translation=translation * 1000,
                                       geomtranslation=geomtranslation * 1000,
                                       cubicalbound=cubicalbound,
                                       trapezoidalbound=trapezoidalbound,
                                       geant4RegistryAdd=g4add,
                                       flukaConvert=flukaConvert,
                                       prototype=prototype)
        if element.category == "rbend":
            return self.MakeFlukaRBend(name=element.name,
                                       element=element,
                                       rotation=rotation,
                                       translation=translation * 1000,
                                       geomtranslation=geomtranslation * 1000,
                                       cubicalbound=cubicalbound,
                                       trapezoidalbound=trapezoidalbound,
                                       geant4RegistryAdd=g4add,
                                       flukaConvert=flukaConvert,
                                       prototype=prototype)
        if element.category == "sbend":
            return self.MakeFlukaSBend(name=element.name,
                                       element=element,
                                       rotation=rotation,
                                       translation=translation * 1000,
                                       geomtranslation=geomtranslation * 1000,
                                       cubicalbound=cubicalbound,
                                       trapezoidalbound=trapezoidalbound,
                                       geant4RegistryAdd=g4add,
                                       flukaConvert=flukaConvert,
                                       prototype=prototype)
        elif element.category == "quadrupole":
            return self.MakeFlukaQuadrupole(name=element.name,
                                            element=element,
                                            rotation=rotation,
                                            translation=translation * 1000,
                                            geomtranslation=geomtranslation * 1000,
                                            cubicalbound=cubicalbound,
                                            trapezoidalbound=trapezoidalbound,
                                            geant4RegistryAdd=g4add,
                                            flukaConvert=flukaConvert,
                                            prototype=prototype)
        elif element.category == "sextupole":
            return self.MakeFlukaSextupole(name=element.name,
                                           element=element,
                                           rotation=rotation,
                                           translation=translation * 1000,
                                           geomtranslation=geomtranslation * 1000,
                                           cubicalbound=cubicalbound,
                                           trapezoidalbound=trapezoidalbound,
                                           geant4RegistryAdd=g4add,
                                           flukaConvert=flukaConvert,
                                           prototype=prototype)
        elif element.category == "octupole":
            return self.MakeFlukaOctupole(name=element.name,
                                          element=element,
                                          rotation=rotation,
                                          translation=translation * 1000,
                                          geomtranslation=geomtranslation * 1000,
                                          cubicalbound=cubicalbound,
                                          trapezoidalbound=trapezoidalbound,
                                          geant4RegistryAdd=g4add,
                                          flukaConvert=flukaConvert,
                                          prototype=prototype)
        elif element.category == "decapole":
            return self.MakeFlukaDecapole(name=element.name,
                                          element=element,
                                          rotation=rotation,
                                          translation=translation * 1000,
                                          geomtranslation=geomtranslation * 1000,
                                          cubicalbound=cubicalbound,
                                          trapezoidalbound=trapezoidalbound,
                                          geant4RegistryAdd=g4add,
                                          flukaConvert=flukaConvert,
                                          prototype=prototype)
        elif element.category == "target":
            return self.MakeFlukaTarget(name=element.name,
                                        element=element,
                                        rotation=rotation,
                                        translation=translation * 1000,
                                        geomtranslation=geomtranslation * 1000,
                                        cubicalbound=cubicalbound,
                                        trapezoidalbound=trapezoidalbound,
                                        geant4RegistryAdd=g4add,
                                        flukaConvert=flukaConvert,
                                        prototype=prototype)
        elif element.category == "rcol":
            return self.MakeFlukaRCol(name=element.name,
                                      element=element,
                                      rotation=rotation,
                                      translation=translation * 1000,
                                      geomtranslation=geomtranslation * 1000,
                                      cubicalbound=cubicalbound,
                                      trapezoidalbound=trapezoidalbound,
                                      geant4RegistryAdd=g4add,
                                      flukaConvert=flukaConvert,
                                      prototype=prototype)
        elif element.category == "ecol":
            return self.MakeFlukaECol(name=element.name,
                                      element=element,
                                      rotation=rotation,
                                      translation=translation * 1000,
                                      geomtranslation=geomtranslation * 1000,
                                      cubicalbound=cubicalbound,
                                      trapezoidalbound=trapezoidalbound,
                                      geant4RegistryAdd=g4add,
                                      flukaConvert=flukaConvert,
                                      prototype=prototype)
        elif element.category == "jcol":
            return self.MakeFlukaJCol(name=element.name,
                                      element=element,
                                      rotation=rotation,
                                      translation=translation * 1000,
                                      geomtranslation=geomtranslation * 1000,
                                      cubicalbound=cubicalbound,
                                      trapezoidalbound=trapezoidalbound,
                                      geant4RegistryAdd=g4add,
                                      flukaConvert=flukaConvert,
                                      prototype=prototype)
        elif element.category == "shield":
            return self.MakeFlukaShield(name=element.name,
                                        element=element,
                                        rotation=rotation,
                                        translation=translation * 1000,
                                        geomtranslation=geomtranslation * 1000,
                                        cubicalbound=cubicalbound,
                                        trapezoidalbound=trapezoidalbound,
                                        geant4RegistryAdd=g4add,
                                        flukaConvert=flukaConvert,
                                        prototype=prototype)
        elif element.category == "dump":
            return self.MakeFlukaDump(name=element.name,
                                      element=element,
                                      rotation=rotation,
                                      translation=translation * 1000,
                                      geomtranslation=geomtranslation * 1000,
                                      cubicalbound=cubicalbound,
                                      trapezoidalbound=trapezoidalbound,
                                      geant4RegistryAdd=g4add,
                                      flukaConvert=flukaConvert,
                                      prototype=prototype)
        elif element.category == "wirescanner":
            return self.MakeFlukaWireScanner(name=element.name,
                                             element=element,
                                             rotation=rotation,
                                             translation=translation * 1000,
                                             geomtranslation=geomtranslation * 1000,
                                             cubicalbound=cubicalbound,
                                             trapezoidalbound=trapezoidalbound,
                                             geant4RegistryAdd=g4add,
                                             flukaConvert=flukaConvert,
                                             prototype=prototype)
        elif element.category == "gap":
            return self.MakeFlukaGap(name=element.name,
                                     element=element,
                                     rotation=rotation,
                                     translation=translation * 1000,
                                     geomtranslation=geomtranslation * 1000,
                                     cubicalbound=cubicalbound,
                                     trapezoidalbound=trapezoidalbound,
                                     geant4RegistryAdd=g4add,
                                     flukaConvert=flukaConvert,
                                     prototype=prototype)
        elif element.category == "customG4":
            return self.MakeFlukaCustomG4(name=element.name,
                                          element=element,
                                          rotation=rotation,
                                          translation=translation * 1000,
                                          geomtranslation=geomtranslation * 1000,
                                          cubicalbound=cubicalbound,
                                          trapezoidalbound=trapezoidalbound,
                                          geant4RegistryAdd=g4add,
                                          flukaConvert=flukaConvert,
                                          material=None,
                                          prototype=prototype)
        elif element.category == "customFluka":
            return self.MakeFlukaCustomFluka(name=element.name,
                                             element=element,
                                             rotation=rotation,
                                             translation=translation * 1000,
                                             geomtranslation=geomtranslation * 1000,
                                             cubicalbound=cubicalbound,
                                             trapezoidalbound=trapezoidalbound,
                                             flukaConvert=flukaConvert,
                                             prototype=prototype)
        elif element.category == "sampler_plane":
            return self.MakeFlukaSampler(name=element.name,
                                         element=element,
                                         rotation=rotation,
                                         translation=translation * 1000,
                                         geomtranslation=geomtranslation * 1000,
                                         cubicalbound=cubicalbound,
                                         trapezoidalbound=trapezoidalbound,
                                         geant4RegistryAdd=g4add,
                                         flukaConvert=flukaConvert)
        elif element.category == "lattice_instance" :
            return self.MakeFlukaLatticeInstance(name=element.name,
                                                 element=element,
                                                 rotation=rotation,
                                                 translation = translation * 1000,
                                                 geomtranslation = geomtranslation * 1000,
                                                 cubicalbound = cubicalbound,
                                                 trapezoidalbound = trapezoidalbound,
                                                 geant4RegistryAdd = g4add,
                                                 flukaConvert = flukaConvert)
        else :
            print("Element category not recognized: ", element.category)

    def MakeFlukaDrift(self,
                       name,
                       element,
                       rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                       translation = _np.array([0,0,0]),
                       geomtranslation = _np.array([0,0,0]),
                       cubicalbound = None,
                       trapezoidalbound = None,
                       geant4RegistryAdd = False,
                       flukaConvert = True,
                       prototype = False):

        """Build fluka drift objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaDrift: Making drfit element ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        beampipeMaterialName = element["beampipeMaterial"]
        beampipeRadius       = element["beampipeRadius"]
        beampipeThickness    = element["beampipeThickness"]

        vacuumMaterial = element["vacuumMaterial"]

        e1 = element["outerE1"]
        e2 = element["outerE2"]
        p1 = element['outerP1']
        p2 = element['outerP2']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry,
                                                            name = name,
                                                            motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make beampipe
        [bpLogical, bpPhysical, vacPhysical] = _MakeBeamPipeCircular(g4registry,
                                                                     motherLogical=outerLogical,
                                                                     name = name,
                                                                     length=length,
                                                                     beamPipeRadius=beampipeRadius,
                                                                     beamPipeThickness=beampipeThickness,
                                                                     beamPipeMaterialName=beampipeMaterialName,
                                                                     e1=e1, p1=p1, e2=e2, p2=p2)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        return self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                rotation, translation, geomtranslation,
                                                category="drift",
                                                convertMaterials=False,
                                                prototype=prototype)


    def MakeFlukaRBend(self,
                       name,
                       element,
                       rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                       translation = _np.array([0,0,0]),
                       geomtranslation = _np.array([0,0,0]),
                       cubicalbound = None,
                       trapezoidalbound = None,
                       geant4RegistryAdd = False,
                       flukaConvert = True,
                       prototype = False):

        """Build fluka rbend objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaRBend: Making rbend element ", name)

        length = element.length*1000
        angle = element["angle"]

        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        beampipeMaterialName = element["beampipeMaterial"]
        beampipeRadius       = element["beampipeRadius"]
        beampipeThickness    = element["beampipeThickness"]

        vacuumMaterial = element["vacuumMaterial"]

        e1 = element["outerE1"]
        e2 = element["outerE2"]
        p1 = element['outerP1']
        p2 = element['outerP2']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make beampipe
        [bpLogical, bpPhysical, vacPhysical] = _MakeBeamPipeCircular(g4registry, motherLogical=outerLogical,
                                                                     name = name,
                                                                     length=length,
                                                                     beamPipeRadius=beampipeRadius,
                                                                     beamPipeThickness=beampipeThickness,
                                                                     beamPipeMaterialName=beampipeMaterialName,
                                                                     e1=e1, p1=p1, e2=e2, p2=p2)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        ret_dict = self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                    rotation, translation, geomtranslation,
                                                    category="rbend",
                                                    convertMaterials=False,
                                                    prototype=prototype)

        # calculate field strength
        rho = length/(2*_np.sin(angle/2.))
        b_field = self._CalculateDipoleFieldStrength(self.beam.momentum, rho)

        # bookkeeping info for element
        bki = self.elementBookkeeping[element.name]

        # make field transform
        rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
        translation = list(-rotation_inv @ bki['translation'])
        rotation = _matrix2tbxyz(rotation_inv)
        rdi = _rotoTranslationFromTra2("TM"+format(self.flukamgncount, "03"),[rotation, translation])

        # find vacuum region
        vacuum_index = bki['physicalVolumes'].index(vacPhysical.name)
        vacuum_region = bki['flukaRegions'][vacuum_index]

        if not prototype :
            # add transformation to registry
            if len(rdi) > 0 :
                self.flukaregistry.addRotoTranslation(rdi)

            # make and assign field to region(s)
            mgnname = "MG"+format(self.flukamgncount, "03")
            mgnfield = _Mgnfield(strength=-b_field,rotDefini=rdi.name, applyRegion=0,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None,
                                 sdum = mgnname)
            self.AddMgnfield(mgnfield)

            mgncreat = _Mgncreat(fieldType=_Mgncreat.DIPOLE, applicableRadius=0, xOffset=0, yOffset=0, mirrorSymmetry=0, sdum=mgnname)
            self.AddMgncreat(mgncreat)

            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1/1e3, maxStepSize=1.0,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # increment mgn count
            self.flukamgncount += 1

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, mgnname)
        else :
            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1 / 1e3, maxStepSize=0.1,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, "dummy")

        return ret_dict

    def MakeFlukaSBend(self,
                       name,
                       element,
                       rotation = _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                       translation = _np.array([0,0,0]),
                       geomtranslation = _np.array([0,0,0]),
                       cubicalbound = None,
                       trapezoidalbound = None,
                       geant4RegistryAdd = False,
                       flukaConvert = True,
                       prototype = False):

        """Build fluka sbend objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaSBend: Making sbend element ", name)

        length = element.length*1000
        angle = element["angle"]
        chord = 2 * (length / angle) * _np.sin(angle / 2)

        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        beampipeMaterialName = element["beampipeMaterial"]
        beampipeRadius       = element["beampipeRadius"]
        beampipeThickness    = element["beampipeThickness"]

        vacuumMaterial = element["vacuumMaterial"]

        e1 = element["outerE1"]
        e2 = element["outerE2"]
        p1 = element['outerP1']
        p2 = element['outerP2']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name,
                                                            motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make beampipe
        [bpLogical, bpPhysical, vacPhysical] = _MakeBeamPipeCircular(g4registry, motherLogical=outerLogical,
                                                                     name = name,
                                                                     length=chord,
                                                                     beamPipeRadius=beampipeRadius,
                                                                     beamPipeThickness=beampipeThickness,
                                                                     beamPipeMaterialName=beampipeMaterialName,
                                                                     e1=e1, p1=p1, e2=e2, p2=p2)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        ret_dict = self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                    rotation, translation, geomtranslation,
                                                    category="sbend",
                                                    convertMaterials=False,
                                                    prototype=prototype)

        # calculate field strength
        rho = length/angle

        # calculate field strength
        b_field = self._CalculateDipoleFieldStrength(self.beam.momentum, rho)

        # bookkeeping info for element
        bki = self.elementBookkeeping[element.name]

        # make field transform
        rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
        translation = - rotation_inv @ bki['translation']
        rotation = _matrix2tbxyz(rotation_inv)
        rdi = _rotoTranslationFromTra2("TM"+format(self.flukamgncount, "03"),[rotation, translation])

        # find vacuum region
        vacuum_index = bki['physicalVolumes'].index(vacPhysical.name)
        vacuum_region = bki['flukaRegions'][vacuum_index]

        if not prototype :
            # add transformation to registry
            if len(rdi) > 0 :
                self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

            # make and assign field to region(s)
            mgnname = "MG"+format(self.flukamgncount, "03")
            mgnfield = _Mgnfield(strength=-b_field,rotDefini=rdi.name, applyRegion=0,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None,
                                 sdum = mgnname)
            self.AddMgnfield(mgnfield)

            mgncreat = _Mgncreat(fieldType=_Mgncreat.DIPOLE, applicableRadius=0, xOffset=0, yOffset=0, mirrorSymmetry=0, sdum=mgnname)
            self.AddMgncreat(mgncreat)

            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1/1e3, maxStepSize=0.1,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # increment mgn count
            self.flukamgncount += 1

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, mgnname)
        else :
            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1 / 1e3, maxStepSize=0.1,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, "dummy")


        return ret_dict

    def MakeFlukaQuadrupole(self,
                            name,
                            element,
                            rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                            translation=_np.array([0, 0, 0]),
                            geomtranslation=_np.array([0, 0, 0]),
                            cubicalbound=None,
                            trapezoidalbound=None,
                            geant4RegistryAdd=False,
                            flukaConvert=True,
                            prototype=False):

        """Build fluka quadrupole objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaQuadrupole: Making quadrupole element ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        beampipeMaterialName = element["beampipeMaterial"]
        beampipeRadius       = element["beampipeRadius"]
        beampipeThickness    = element["beampipeThickness"]

        vacuumMaterial = element["vacuumMaterial"]

        e1 = element["outerE1"]
        e2 = element["outerE2"]
        p1 = element['outerP1']
        p2 = element['outerP2']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make beampipe
        [bpLogical, bpPhysical, vacPhysical] = _MakeBeamPipeCircular(g4registry, motherLogical=outerLogical,
                                                                     name = name,
                                                                     length=length,
                                                                     beamPipeRadius=beampipeRadius,
                                                                     beamPipeThickness=beampipeThickness,
                                                                     beamPipeMaterialName=beampipeMaterialName,
                                                                     e1=e1, p1=p1, e2=e2, p2=p2)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        ret_dict = self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                    rotation, translation, geomtranslation,
                                                    category="quad",
                                                    convertMaterials=False,
                                                    prototype=prototype)

        # calculate field strength
        q_over_p = self.beam.charge/self.beam.momentum

        # calculate fluka K
        k1_fluka = element['k1']/q_over_p

        # bookkeeping info for element
        bki = self.elementBookkeeping[element.name]

        # make field transform
        rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
        translation = - rotation_inv @ _np.array(bki['translation'])
        rotation = _matrix2tbxyz(rotation_inv)
        rdi = _rotoTranslationFromTra2("TM"+format(self.flukamgncount, "03"),[rotation, translation])

        # find vacuum region
        vacuum_index = bki['physicalVolumes'].index(vacPhysical.name)
        vacuum_region = bki['flukaRegions'][vacuum_index]

        if not prototype:
            # add transformation to registry
            if len(rdi) > 0 :
                self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

            # make and assign field to region(s)
            mgnname = "MG"+format(self.flukamgncount, "03")
            mgnfield = _Mgnfield(strength=-k1_fluka,rotDefini=rdi.name, applyRegion=0,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None,
                                 sdum = mgnname)
            self.AddMgnfield(mgnfield)

            mgncreat = _Mgncreat(fieldType=_Mgncreat.QUADRUPOLE, applicableRadius=0, xOffset=0, yOffset=0, mirrorSymmetry=0, sdum=mgnname)
            self.AddMgncreat(mgncreat)

            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1/1e3, maxStepSize=0.1, # TODO needs to be user adjustable
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # increment mgn count
            self.flukamgncount += 1

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, mgnname)
        else :
            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1 / 1e3, maxStepSize=0.1,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, "dummy")

        return ret_dict

    def MakeFlukaSextupole(self,
                           name,
                           element,
                           rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                           translation=_np.array([0, 0, 0]),
                           geomtranslation=_np.array([0, 0, 0]),
                           cubicalbound=None,
                           trapezoidalbound=None,
                           geant4RegistryAdd=False,
                           flukaConvert=True,
                           prototype=False):

        """Build fluka sextupole objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaSextupole: Making sextupole element ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        beampipeMaterialName = element["beampipeMaterial"]
        beampipeRadius       = element["beampipeRadius"]
        beampipeThickness    = element["beampipeThickness"]

        vacuumMaterial = element["vacuumMaterial"]

        e1 = element["outerE1"]
        e2 = element["outerE2"]
        p1 = element['outerP1']
        p2 = element['outerP2']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make beampipe
        [bpLogical, bpPhysical, vacPhysical] = _MakeBeamPipeCircular(g4registry, motherLogical=outerLogical,
                                                                     name = name,
                                                                     length=length,
                                                                     beamPipeRadius=beampipeRadius,
                                                                     beamPipeThickness=beampipeThickness,
                                                                     beamPipeMaterialName=beampipeMaterialName,
                                                                     e1=e1, p1=p1, e2=e2, p2=p2)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        ret_dict = self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                    rotation, translation, geomtranslation,
                                                    category="sextu",
                                                    convertMaterials=False,
                                                    prototype=prototype)

        # calculate field strength
        q_over_p = self.beam.charge/self.beam.momentum

        # calculate fluka K
        k2_fluka = element['k2']/q_over_p

        # bookkeeping info for element
        bki = self.elementBookkeeping[element.name]

        # make field transform
        rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
        translation = - rotation_inv @ _np.array(bki['translation'])
        rotation = _matrix2tbxyz(rotation_inv)
        rdi = _rotoTranslationFromTra2("TM"+format(self.flukamgncount, "03"),[rotation, translation])

        # find vacuum region
        vacuum_index = bki['physicalVolumes'].index(vacPhysical.name)
        vacuum_region = bki['flukaRegions'][vacuum_index]

        if not prototype:
            # add transformation to registry
            if len(rdi) > 0 :
                self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

            # make and assign field to region(s)
            mgnname = "MG"+format(self.flukamgncount, "03")
            mgnfield = _Mgnfield(strength=-k2_fluka,rotDefini=rdi.name, applyRegion=0,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None,
                                 sdum = mgnname)
            self.AddMgnfield(mgnfield)

            mgncreat = _Mgncreat(fieldType=_Mgncreat.SEXTUPOLE, applicableRadius=0, xOffset=0, yOffset=0, mirrorSymmetry=0, sdum=mgnname)
            self.AddMgncreat(mgncreat)

            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1/1e3, maxStepSize=0.1, # TODO needs to be user adjustable
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # increment mgn count
            self.flukamgncount += 1

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, mgnname)
        else :
            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1 / 1e3, maxStepSize=0.1,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, "dummy")

        return ret_dict

    def MakeFlukaOctupole(self,
                          name,
                          element,
                          rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                          translation=_np.array([0, 0, 0]),
                          geomtranslation=_np.array([0, 0, 0]),
                          cubicalbound=None,
                          trapezoidalbound=None,
                          geant4RegistryAdd=False,
                          flukaConvert=True,
                          prototype=False):

        """Build fluka octupole objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaOctupole: Making octupole element ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        beampipeMaterialName = element["beampipeMaterial"]
        beampipeRadius       = element["beampipeRadius"]
        beampipeThickness    = element["beampipeThickness"]

        vacuumMaterial = element["vacuumMaterial"]

        e1 = element["outerE1"]
        e2 = element["outerE2"]
        p1 = element['outerP1']
        p2 = element['outerP2']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make beampipe
        [bpLogical, bpPhysical, vacPhysical] = _MakeBeamPipeCircular(g4registry, motherLogical=outerLogical,
                                                                     name = name,
                                                                     length=length,
                                                                     beamPipeRadius=beampipeRadius,
                                                                     beamPipeThickness=beampipeThickness,
                                                                     beamPipeMaterialName=beampipeMaterialName,
                                                                     e1=e1, p1=p1, e2=e2, p2=p2)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        ret_dict = self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                    rotation, translation, geomtranslation,
                                                    category="octu",
                                                    convertMaterials=False,
                                                    prototype=prototype)

        # calculate field strength
        q_over_p = self.beam.charge/self.beam.momentum

        # calculate fluka K
        k3_fluka = element['k3']/q_over_p

        # bookkeeping info for element
        bki = self.elementBookkeeping[element.name]

        # make field transform
        rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
        translation = - rotation_inv @ _np.array(bki['translation'])
        rotation = _matrix2tbxyz(rotation_inv)
        rdi = _rotoTranslationFromTra2("TM"+format(self.flukamgncount, "03"),[rotation, translation])

        # find vacuum region
        vacuum_index = bki['physicalVolumes'].index(vacPhysical.name)
        vacuum_region = bki['flukaRegions'][vacuum_index]

        if not prototype:
            # add transformation to registry
            if len(rdi) > 0 :
                self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

            # make and assign field to region(s)
            mgnname = "MG"+format(self.flukamgncount, "03")
            mgnfield = _Mgnfield(strength=-k3_fluka,rotDefini=rdi.name, applyRegion=0,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None,
                                 sdum = mgnname)
            self.AddMgnfield(mgnfield)

            mgncreat = _Mgncreat(fieldType=_Mgncreat.OCTUPOLE, applicableRadius=0, xOffset=0, yOffset=0, mirrorSymmetry=0, sdum=mgnname)
            self.AddMgncreat(mgncreat)

            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1/1e3, maxStepSize=0.1, # TODO needs to be user adjustable
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # increment mgn count
            self.flukamgncount += 1

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, mgnname)
        else :
            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1 / 1e3, maxStepSize=0.1,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, "dummy")

        return ret_dict

    def MakeFlukaDecapole(self,
                          name,
                          element,
                          rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                          translation=_np.array([0, 0, 0]),
                          geomtranslation=_np.array([0, 0, 0]),
                          cubicalbound=None,
                          trapezoidalbound=None,
                          geant4RegistryAdd=False,
                          flukaConvert=True,
                          prototype=False):

        """Build fluka decapole objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaDecapole: Making decapole element ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        beampipeMaterialName = element["beampipeMaterial"]
        beampipeRadius       = element["beampipeRadius"]
        beampipeThickness    = element["beampipeThickness"]

        vacuumMaterial = element["vacuumMaterial"]

        e1 = element["outerE1"]
        e2 = element["outerE2"]
        p1 = element['outerP1']
        p2 = element['outerP2']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make beampipe
        [bpLogical, bpPhysical, vacPhysical] = _MakeBeamPipeCircular(g4registry, motherLogical=outerLogical,
                                                                     name = name,
                                                                     length=length,
                                                                     beamPipeRadius=beampipeRadius,
                                                                     beamPipeThickness=beampipeThickness,
                                                                     beamPipeMaterialName=beampipeMaterialName,
                                                                     e1=e1, p1=p1, e2=e2, p2=p2)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        ret_dict = self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                    rotation, translation, geomtranslation,
                                                    category="deca",
                                                    convertMaterials=False,
                                                    prototype=prototype)

        # calculate field strength
        q_over_p = self.beam.charge/self.beam.momentum

        # calculate fluka K
        k4_fluka = element['k4']/q_over_p

        # bookkeeping info for element
        bki = self.elementBookkeeping[element.name]

        # make field transform
        rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
        translation = - rotation_inv @ _np.array(bki['translation'])
        rotation = _matrix2tbxyz(rotation_inv)
        rdi = _rotoTranslationFromTra2("TM"+format(self.flukamgncount, "03"),[rotation, translation])

        # find vacuum region
        vacuum_index = bki['physicalVolumes'].index(vacPhysical.name)
        vacuum_region = bki['flukaRegions'][vacuum_index]

        if not prototype:
            # add transformation to registry
            if len(rdi) > 0 :
                self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

            # make and assign field to region(s)
            mgnname = "MG"+format(self.flukamgncount, "03")
            mgnfield = _Mgnfield(strength=-k4_fluka,rotDefini=rdi.name, applyRegion=0,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None,
                                 sdum = mgnname)
            self.AddMgnfield(mgnfield)

            mgncreat = _Mgncreat(fieldType=_Mgncreat.DECAPOLE, applicableRadius=0, xOffset=0, yOffset=0, mirrorSymmetry=0, sdum=mgnname)
            self.AddMgncreat(mgncreat)

            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1/1e3, maxStepSize=0.1, # TODO needs to be user adjustable
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # increment mgn count
            self.flukamgncount += 1

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, mgnname)
        else :
            # add stepsize
            stepsize = _Stepsize(minStepSize=-0.1 / 1e3, maxStepSize=0.1,
                                 regionFrom=vacuum_region, regionTo=None, regionStep=None)
            self.AddStepsize(stepsize)

            # add magnetic field to assimat
            self.flukaregistry.assignmaAddMagnetic(vacuum_region, "dummy")

        return ret_dict

    def MakeFlukaTarget(self,
                        name,
                        element,
                        rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                        translation=_np.array([0, 0, 0]),
                        geomtranslation=_np.array([0, 0, 0]),
                        cubicalbound=None,
                        trapezoidalbound=None,
                        geant4RegistryAdd=False,
                        flukaConvert=True,
                        prototype=False):

        """Build fluka target objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaTarget: Making target element ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        targetMaterial       = element["material"]
        targetApertureType   = element["apertureType"]
        targetHorizontalSize = element["horizontalWidth"]
        targetVerticalSize   = element["verticalWidth"]

        e1 = element["outerE1"]
        e2 = element["outerE2"]
        p1 = element['outerP1']
        p2 = element['outerP2']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make beampipe
        [targetLogical, targetPhysical] = _MakeTarget(g4registry,
                                                      motherLogical=outerLogical,
                                                      name=name,
                                                      apertureType=targetApertureType,
                                                      length=length,
                                                      material=targetMaterial,
                                                      horizontalWidth=targetHorizontalSize,
                                                      verticalWidth=targetVerticalSize)


        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        return self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                rotation, translation, geomtranslation,
                                                category="target",
                                                convertMaterials=False,
                                                prototype=prototype)

    def MakeFlukaRCol(self,
                      name,
                      element,
                      rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                      translation=_np.array([0, 0, 0]),
                      geomtranslation=_np.array([0, 0, 0]),
                      cubicalbound=None,
                      trapezoidalbound=None,
                      geant4RegistryAdd=False,
                      flukaConvert=True,
                      prototype=False):

        """Build fluka rcol objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaRCol: Making ecol element ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        horizontalWidth = element['horizontalWidth']
        verticalWidth   = element['verticalWidth']
        material        = element['material']
        xsize           = element['xsize']
        ysize           = element['ysize']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make collimator
        [rcolLogical, rcolPhysical] = _MakeRCol(g4registry, name=name, motherLogical=outerLogical,
                                                length=length,
                                                material=material,
                                                horizontalWidth=horizontalWidth,
                                                verticalWidth=verticalWidth,
                                                xsize=xsize,
                                                ysize=ysize)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        return self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                rotation, translation, geomtranslation,
                                                category="rcol",
                                                convertMaterials=False,
                                                prototype=prototype)

    def MakeFlukaECol(self,
                      name,
                      element,
                      rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                      translation=_np.array([0, 0, 0]),
                      geomtranslation=_np.array([0, 0, 0]),
                      cubicalbound=None,
                      trapezoidalbound=None,
                      geant4RegistryAdd=False,
                      flukaConvert=True,
                      prototype=False):

        """Build fluka ecol objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaECol: Making target ecol ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        horizontalWidth = element['horizontalWidth']
        verticalWidth   = element['verticalWidth']
        material        = element['material']
        xsize           = element['xsize']
        ysize           = element['ysize']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make collimator
        [ecolLogical, ecolPhysical] = _MakeECol(g4registry,
                                                name=name,
                                                motherLogical=outerLogical,
                                                length=length,
                                                material=material,
                                                horizontalWidth=horizontalWidth,
                                                verticalWidth=verticalWidth,
                                                xsize=xsize,
                                                ysize=ysize)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        return self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                rotation, translation, geomtranslation,
                                                category="ecol",
                                                convertMaterials=False,
                                                prototype=prototype)

    def MakeFlukaJCol(self,
                      name,
                      element,
                      rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                      translation=_np.array([0, 0, 0]),
                      geomtranslation=_np.array([0, 0, 0]),
                      cubicalbound=None,
                      trapezoidalbound=None,
                      geant4RegistryAdd=False,
                      flukaConvert=True,
                      prototype=False):

        """Build fluka jcol objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaJCol: Making target jcol ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        xsize           = element['xsize']
        ysize           = element['ysize']
        xsizeLeft       = element['xsizeLeft']
        xsizeRight      = element['xsizeRight']
        jawTiltLeft     = element['jawTiltLeft']
        jawTiltRight    = element['jawTiltRight']
        horizontalWidth = element['horizontalWidth']
        verticalWidth   = element['verticalWidth']
        material        = element['material']

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make collimator
        [jcolLeftLogical, jcolLeftPhysical], [jcolRightLogical, jcolRightPhysical] \
            = _MakeJCol(g4registry,
                        name=name,
                        motherLogical=outerLogical,
                        length=length,
                        material=material,
                        horizontalWidth=horizontalWidth,
                        verticalWidth=verticalWidth,
                        xsize=xsize,
                        ysize=ysize,
                        xsizeLeft=xsizeLeft,
                        xsizeRight=xsizeRight,
                        jawTiltLeft=jawTiltLeft,
                        jawTiltRight=jawTiltRight)


        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        return self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                rotation, translation, geomtranslation,
                                                category="jcol",
                                                convertMaterials=False,
                                                prototype=prototype)


    def MakeFlukaShield(self,
                        name,
                        element,
                        rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                        translation=_np.array([0, 0, 0]),
                        geomtranslation=_np.array([0, 0, 0]),
                        cubicalbound=None,
                        trapezoidalbound=None,
                        geant4RegistryAdd=False,
                        flukaConvert=True,
                        prototype=False):

        """Build fluka shield objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaShield: Making target shield ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        beampipeMaterialName = element["beampipeMaterial"]
        beampipeRadius       = element["beampipeRadius"]
        beampipeThickness    = element["beampipeThickness"]

        vacuumMaterial = element["vacuumMaterial"]

        e1 = element["outerE1"]
        e2 = element["outerE2"]
        p1 = element['outerP1']
        p2 = element['outerP2']

        horizontalWidth = element["horizontalWidth"]
        verticalWidth   = element["verticalWidth"]
        xsize           = element["xsize"]
        ysize           = element["ysize"]
        material        = element["material"]

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make beampipe
        [bpLogical, bpPhysical, vacPhysical] = _MakeBeamPipeCircular(g4registry, motherLogical=outerLogical,
                                                                     name = name,
                                                                     length=length,
                                                                     beamPipeRadius=beampipeRadius,
                                                                     beamPipeThickness=beampipeThickness,
                                                                     beamPipeMaterialName=beampipeMaterialName,
                                                                     e1=e1, p1=p1, e2=e2, p2=p2)

        # make shield
        [shieldLogical, shieldPhysical] = _MakeShield(g4registry,
                                                      name=name,
                                                      motherLogical=outerLogical,
                                                      length=length,
                                                      material=material,
                                                      horizontalWidth=horizontalWidth,
                                                      verticalWidth=verticalWidth,
                                                      xsize=xsize,
                                                      ysize=ysize)


        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        return self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                rotation, translation, geomtranslation,
                                                category="shield",
                                                convertMaterials=False,
                                                prototype=prototype)


    def MakeFlukaDump(self,
                      name,
                      element,
                      rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                      translation=_np.array([0, 0, 0]),
                      geomtranslation=_np.array([0, 0, 0]),
                      cubicalbound=None,
                      trapezoidalbound=None,
                      geant4RegistryAdd=False,
                      flukaConvert=True,
                      prototype=False):

        """Build fluka dump objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaDump: Making dump ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        # material = element["material"]
        horizontalWidth = element["horizontalWidth"]
        verticalWidth   = element["verticalWidth"]
        apertureType    = element["apertureType"]

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make dump
        [dumpLogical, dumpPhysical] = _MakeDump(g4registry,
                                                name=name,
                                                motherLogical=outerLogical,
                                                length=length,
                                                material="BLCKHOLE",
                                                horizontalWidth=horizontalWidth,
                                                verticalWidth=verticalWidth,
                                                apertureType=apertureType)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        return self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                rotation, translation, geomtranslation,
                                                category="dump",
                                                convertMaterials=False,
                                                prototype=prototype)


    def MakeFlukaWireScanner(self,
                             name,
                             element,
                             rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                             translation=_np.array([0, 0, 0]),
                             geomtranslation=_np.array([0, 0, 0]),
                             cubicalbound=None,
                             trapezoidalbound=None,
                             geant4RegistryAdd=False,
                             flukaConvert=True,
                             prototype=False):

        """Build fluka wire scanner objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaWireScanner: Making wirescanner ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        e1 = element["outerE1"]
        e2 = element["outerE2"]
        p1 = element['outerP1']
        p2 = element['outerP2']

        beampipeMaterialName = element["beampipeMaterial"]
        beampipeRadius       = element["beampipeRadius"]
        beampipeThickness    = element["beampipeThickness"]
        vacuumMaterial       = element["vacuumMaterial"]

        wireMaterial = element["wireMaterial"]
        wireDiameter = element["wireDiameter"]
        wireLength   = element["wireLength"]
        wireAngle    = element["wireAngle"]
        wireOffsetX  = element["wireOffsetX"]
        wireOffsetY  = element["wireOffsetY"]
        wireOffsetZ  = element["wireOffsetZ"]

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry,
                                                            name = name,
                                                            motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        # make beampipe
        [bpLogical, bpPhysical, vacPhysical] = _MakeBeamPipeCircular(g4registry,
                                                                     motherLogical=outerLogical,
                                                                     name = name,
                                                                     length=length,
                                                                     beamPipeRadius=beampipeRadius,
                                                                     beamPipeThickness=beampipeThickness,
                                                                     beamPipeMaterialName=beampipeMaterialName,
                                                                     e1=e1, p1=p1, e2=e2, p2=p2)

        # make wire
        [wireLogical, wirePhysical] = _MakeWireScanner(g4registry,
                                                        name=name,
                                                        motherLogical=bpLogical.daughterVolumes[0].logicalVolume,
                                                        wireMaterial=wireMaterial,
                                                        wireDiameter=wireDiameter,
                                                        wireLength=wireLength,
                                                        wireAngle=wireAngle,
                                                        wireOffsetX=wireOffsetX,
                                                        wireOffsetY=wireOffsetY,
                                                        wireOffsetZ=wireOffsetZ)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        return self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                rotation, translation, geomtranslation,
                                                category="wirescanner",
                                                convertMaterials=False,
                                                prototype=prototype)

    def MakeFlukaGap(self,
                     name,
                     element,
                     rotation=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                     translation=_np.array([0, 0, 0]),
                     geomtranslation=_np.array([0, 0, 0]),
                     cubicalbound=None,
                     trapezoidalbound=None,
                     geant4RegistryAdd=False,
                     flukaConvert=True,
                     prototype=False):

        """Build fluka gap objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaGap: Making target gap ", name)

        length = element.length*1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=outerVerticalSize,
                                                            outerMaterial=outerMaterial)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        return self._MakeFlukaComponentCommonG4(name,outerLogical, outerPhysical, flukaConvert,
                                                rotation, translation, geomtranslation,
                                                category="gap",
                                                convertMaterials=False,
                                                prototype=prototype)

    def MakeFlukaSampler(self,
                         name,
                         element,
                         rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                         translation = _np.array([0,0,0]),
                         geomtranslation = _np.array([0,0,0]),
                         cubicalbound = None,
                         trapezoidalbound = None,
                         geant4RegistryAdd = False,
                         flukaConvert = True,
                         material=None):
        """Build fluka sampler objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaSampler: Making sampler element ", name)


        if not material:
            material = self.options.samplerMaterial

        length = element.length*1000
        rotation, geomtranslation = self._MakeOffsetAndTiltTransforms(element, rotation, geomtranslation)
        samplerMaterialName = element["samplerMaterial"]
        samplerDiameter = element["samplerDiameter"]
        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # make fake geant4 materials for conversion
        samplerMaterial = _pyg4.geant4.MaterialSingleElement(name=samplerMaterialName, atomic_number=1, atomic_weight=1, density=1)

        # make box of correct size
        samplersolid    = _pyg4.geant4.solid.Box(name+"_solid",samplerDiameter,samplerDiameter,length,g4registry)
        samplerlogical  = _pyg4.geant4.LogicalVolume(samplersolid,samplerMaterial,name+"_lv",g4registry)
        samplerphysical = _pyg4.geant4.PhysicalVolume([0,0,0],
                                                      [0,0,0],
                                                      samplerlogical,
                                                      name+"_pv",
                                                      self.worldLogical,
                                                      g4registry)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        return self._MakeFlukaComponentCommonG4(name,samplerlogical, samplerphysical, flukaConvert,
                                                rotation, translation, geomtranslation,
                                                category="sampler",
                                                convertMaterials=False,
                                                prototype=False)

    def MakeFlukaCustomG4(self,
                          name,
                          element,
                          rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                          translation = _np.array([0,0,0]),
                          geomtranslation = _np.array([0,0,0]),
                          cubicalbound = None,
                          trapezoidalbound = None,
                          geant4RegistryAdd = False,
                          flukaConvert = True,
                          material=None,
                          prototype=False
                    ):

        # length
        """Build fluka custom g4 objects for geometry conversion and export."""
        length = element.length * 1000
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        # keyword arguments
        outerHorizontalSize = element["outerHorizontalSize"]
        outerVerticalSize   = element["outerVerticalSize"]
        outerMaterial       = element["outerMaterial"]

        # registry
        g4registry = self._GetGeant4Registry(geant4RegistryAdd)

        # custom geometry LV
        customContainerLV = element['containerLV']

        # convert materials from geant4
        _pyg4.convert.geant42Fluka.geant4MaterialDict2Fluka(g4registry.materialDict,
                                                            self._GetFlukaRegistry(flukaRegistryAdd=True))

        # make outer volume
        [outerLogical, outerPhysical] = _MakeOuterTrapezoid(g4registry, name = name, motherLogical=self.worldLogical,
                                                            tra_coords=trapezoidalbound*1000,
                                                            outerVerticalSize=5000,
                                                            outerMaterial=outerMaterial)

        customContainerPV = _pyg4.geant4.PhysicalVolume([0, 0, 0],
                                                        [0, 0, 0],
                                                        customContainerLV,
                                                        customContainerLV.name+"_pv",
                                                        outerLogical,
                                                        g4registry)

        # take custom LV as outer
        outerLogical = customContainerLV
        outerPhysical = customContainerPV

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        self._MakeFlukaComponentCommonG4(name, outerLogical, outerPhysical, flukaConvert,
                                         rotation, translation, geomtranslation, "customg4",
                                         convertMaterials=False,
                                         prototype=prototype)

    def MakeFlukaCustomFluka(self, name, element,
                             rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                             translation = _np.array([0,0,0]),
                             geomtranslation = _np.array([0,0,0]),
                             cubicalbound=None,
                             trapezoidalbound=None,
                             geant4RegistryAdd=False,
                             flukaConvert=True,
                             prototype=False):

        """Build fluka custom fluka objects for geometry conversion and export."""
        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        regionNamesTransferred = []

        outer_region  = element['customOuterRegion']
        outer_bodies  = element["customOuterBodies"]
        regions       = element["customRegions"]
        flukaRegistry = element['flukaRegistry']

        if flukaConvert:
            # cut out regions for placement
            for body in outer_bodies:
                z = _pyg4.fluka.Zone()
                z.addIntersection(body)
                if not prototype :
                    self.worldzone.addSubtraction(z)
                else :
                    self.parkingzone.addSubtraction(z)

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
                fluka_registry = element['flukaRegistry']

                mat = fluka_registry.assignmas[region.name]
                self._GetFlukaRegistry(True).addMaterialAssignments(mat[0],region.name)

        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        self._MakeFlukaComponentCommonFluka(name, regionNamesTransferred, element.category)

    def MakeFlukaLatticeInstance(self,
                                 name,
                                 element,
                                 rotation = _np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]]),
                                 translation = _np.array([0,0,0]),
                                 geomtranslation = _np.array([0,0,0]),
                                 cubicalbound = None,
                                 trapezoidalbound = None,
                                 geant4RegistryAdd = False,
                                 flukaConvert = True,
                                 material=None):
        """Build fluka lattice instance objects for geometry conversion and export."""
        if self.verbose :
            print("pyflubl.BuilderNew.Machine.MakeFlukaLatticeInstance: Making lattice instance element ", name)


        # tilt and shift transforms
        geomtranslation = geomtranslation +  rotation @ _np.array([element['offsetX'], element['offsetY'], 0])

        rotation, translation = self._MakeOffsetAndTiltTransforms(element, rotation, translation)

        # add bookkeeping information for prototype
        self._AddBookkeepingTransformation(name, rotation, translation, geomtranslation)

        # make the prototype if it not found in the book keeping information
        if element['prototype'].name not in self.elementBookkeeping :
            # create prototype at in the parking lot (at displaced location from normal beamline)
            self.elementBookkeeping[element['prototype'].name] = {}

            # advance prototype position based on length
            self.prototype_position[2] += element['prototype'].length*100*1.5

            self.ElementFactory(element['prototype'],
                                _np.eye(3),
                                _np.array(self.prototype_position)/100,
                                _np.array(self.prototype_position)/100,
                                cubicalbound,
                                trapezoidalbound,
                                geant4RegistryAdd,
                                flukaConvert=flukaConvert,
                                prototype=True)

            # need to set dummy S and real length
            self.elementBookkeeping[element['prototype'].name]['S'] = -1.0
            self.elementBookkeeping[element['prototype'].name]['length'] = element['prototype'].length

        # create same body in accelerator
        prototype_bki = self.elementBookkeeping[element['prototype'].name]
        instance_bki = self.elementBookkeeping[element.name]

        # Geant4 prototype
        if 'outerPhysicalVolume' in prototype_bki:
            # get prototype bookkeeping information
            pv_name = prototype_bki['outerPhysicalVolume']
            pv = _copy.copy(self.g4registry.physicalVolumeDict[pv_name])  # get pv

            # empty daughters as they do not need to be converted
            pv.logicalVolume.daughterVolumes = []

            # rotation as x aligned
            rotation = rotation @ _tbxyz2matrix(pv.rotation.eval())

            # convert geant4 outer to fluka
            flukaouterregion, self.flukanamecount = _geant4PhysicalVolume2Fluka(pv,
                                                                                mtra=rotation,
                                                                                tra=geomtranslation,
                                                                                flukaRegistry=self.flukaregistry,
                                                                                flukaNameCount=self.flukanamecount,
                                                                                bakeTransforms=self.bakeTransforms)

            # cut volume out of mother zone
            for daughterzones in flukaouterregion.zones:
                self.worldzone.addSubtraction(daughterzones)

            # make the assignma material vacuum
            self.flukaregistry.assignmaAddMaterial(flukaouterregion.name, "VACUUM")

            # create instance magnetic fields
            if element['prototype'].category == "sbend" :

                length = element['prototype'].length * 1000
                angle = element['prototype']["angle"]

                # calculate radius of curvature
                rho = length / angle

                # calculate field strength
                b_field = self._CalculateDipoleFieldStrength(self.beam.momentum, rho)

                # bookkeeping info for element
                bki = self.elementBookkeeping[element.name]

                # make field transform
                rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
                translation = - rotation_inv @ bki['translation']
                rotation = _matrix2tbxyz(rotation_inv)
                rdi = _rotoTranslationFromTra2("TM" + format(self.flukamgncount, "03"), [rotation, translation])

                if len(rdi) > 0:
                    self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

                # make and assign field to region(s)
                mgnname = "MG" + format(self.flukamgncount, "03")
                mgnfield = _Mgnfield(strength=-b_field, rotDefini=rdi.name, applyRegion=0,
                                     regionFrom=flukaouterregion.name, regionTo=None, regionStep=None,
                                     sdum=mgnname)
                self.AddMgnfield(mgnfield)

                mgncreat = _Mgncreat(fieldType=_Mgncreat.DIPOLE, applicableRadius=0, xOffset=0, yOffset=0,
                                     mirrorSymmetry=0, sdum=mgnname)
                self.AddMgncreat(mgncreat)

                # increment mgn count
                self.flukamgncount += 1
            elif element['prototype'].category == "rbend" :

                length = element['prototype'].length * 1000
                angle = element['prototype']["angle"]

                # calculate radius of curvature
                rho = length / (2 * _np.sin(angle / 2.))

                # calculate field strength
                b_field = self._CalculateDipoleFieldStrength(self.beam.momentum, rho)

                # bookkeeping info for element
                bki = self.elementBookkeeping[element.name]

                # make field transform
                rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
                translation = - rotation_inv @ bki['translation']
                rotation = _matrix2tbxyz(rotation_inv)
                rdi = _rotoTranslationFromTra2("TM" + format(self.flukamgncount, "03"), [rotation, translation])

                if len(rdi) > 0:
                    self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

                # make and assign field to region(s)
                mgnname = "MG" + format(self.flukamgncount, "03")
                mgnfield = _Mgnfield(strength=-b_field, rotDefini=rdi.name, applyRegion=0,
                                     regionFrom=flukaouterregion.name, regionTo=None, regionStep=None,
                                     sdum=mgnname)
                self.AddMgnfield(mgnfield)

                mgncreat = _Mgncreat(fieldType=_Mgncreat.DIPOLE, applicableRadius=0, xOffset=0, yOffset=0,
                                     mirrorSymmetry=0, sdum=mgnname)
                self.AddMgncreat(mgncreat)

                # increment mgn count
                self.flukamgncount += 1
            elif element['prototype'].category == "quadrupole":

                # calculate field strength
                q_over_p = self.beam.charge / self.beam.momentum

                # calculate fluka K
                k1_fluka = element['prototype']['k1'] / q_over_p

                # bookkeeping info for element
                bki = self.elementBookkeeping[element.name]

                # make field transform
                rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
                translation = -rotation_inv @ _np.array(bki['translation'])
                rotation = _matrix2tbxyz(rotation_inv)
                rdi = _rotoTranslationFromTra2("TM" + format(self.flukamgncount, "03"), [rotation, translation])

                # add transformation to registry
                if len(rdi) > 0 :
                    self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

                # make and assign field to region(s)
                mgnname = "MG"+format(self.flukamgncount, "03")
                mgnfield = _Mgnfield(strength=-k1_fluka,rotDefini=rdi.name, applyRegion=0,
                                     regionFrom=flukaouterregion.name, regionTo=None, regionStep=None,
                                     sdum = mgnname)
                self.AddMgnfield(mgnfield)

                mgncreat = _Mgncreat(fieldType=_Mgncreat.QUADRUPOLE, applicableRadius=0, xOffset=0, yOffset=0, mirrorSymmetry=0, sdum=mgnname)
                self.AddMgncreat(mgncreat)

                # increment mgn count
                self.flukamgncount += 1
            elif element['prototype'].category == "sextupole":

                # calculate field strength
                q_over_p = self.beam.charge / self.beam.momentum

                # calculate fluka K
                k2_fluka = element['prototype']['k2'] / q_over_p

                # bookkeeping info for element
                bki = self.elementBookkeeping[element.name]

                # make field transform
                rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
                translation = -rotation_inv @ _np.array(bki['translation'])
                rotation = _matrix2tbxyz(rotation_inv)
                rdi = _rotoTranslationFromTra2("TM" + format(self.flukamgncount, "03"), [rotation, translation])

                # add transformation to registry
                if len(rdi) > 0 :
                    self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

                # make and assign field to region(s)
                mgnname = "MG"+format(self.flukamgncount, "03")
                mgnfield = _Mgnfield(strength=-k2_fluka,rotDefini=rdi.name, applyRegion=0,
                                     regionFrom=flukaouterregion.name, regionTo=None, regionStep=None,
                                     sdum = mgnname)
                self.AddMgnfield(mgnfield)

                mgncreat = _Mgncreat(fieldType=_Mgncreat.SEXTUPOLE, applicableRadius=0, xOffset=0, yOffset=0, mirrorSymmetry=0, sdum=mgnname)
                self.AddMgncreat(mgncreat)

                # increment mgn count
                self.flukamgncount += 1
            elif element['prototype'].category == "octupole":

                # calculate field strength
                q_over_p = self.beam.charge / self.beam.momentum

                # calculate fluka K
                k3_fluka = element['prototype']['k3'] / q_over_p

                # bookkeeping info for element
                bki = self.elementBookkeeping[element.name]

                # make field transform
                rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
                translation = -rotation_inv @ _np.array(bki['translation'])
                rotation = _matrix2tbxyz(rotation_inv)
                rdi = _rotoTranslationFromTra2("TM" + format(self.flukamgncount, "03"), [rotation, translation])

                # add transformation to registry
                if len(rdi) > 0 :
                    self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

                # make and assign field to region(s)
                mgnname = "MG"+format(self.flukamgncount, "03")
                mgnfield = _Mgnfield(strength=-k3_fluka,rotDefini=rdi.name, applyRegion=0,
                                     regionFrom=flukaouterregion.name, regionTo=None, regionStep=None,
                                     sdum = mgnname)
                self.AddMgnfield(mgnfield)

                mgncreat = _Mgncreat(fieldType=_Mgncreat.OCTUPOLE, applicableRadius=0, xOffset=0, yOffset=0, mirrorSymmetry=0, sdum=mgnname)
                self.AddMgncreat(mgncreat)

                # increment mgn count
                self.flukamgncount += 1
            elif element['prototype'].category == "decapole":

                # calculate field strength
                q_over_p = self.beam.charge / self.beam.momentum

                # calculate fluka K
                k4_fluka = element['prototype']['k4'] / q_over_p

                # bookkeeping info for element
                bki = self.elementBookkeeping[element.name]

                # make field transform
                rotation_inv = _np.linalg.inv(_np.array(bki['rotation']))
                translation = -rotation_inv @ _np.array(bki['translation'])
                rotation = _matrix2tbxyz(rotation_inv)
                rdi = _rotoTranslationFromTra2("TM" + format(self.flukamgncount, "03"), [rotation, translation])

                # add transformation to registry
                if len(rdi) > 0 :
                    self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

                # make and assign field to region(s)
                mgnname = "MG"+format(self.flukamgncount, "03")
                mgnfield = _Mgnfield(strength=-k4_fluka,rotDefini=rdi.name, applyRegion=0,
                                     regionFrom=flukaouterregion.name, regionTo=None, regionStep=None,
                                     sdum = mgnname)
                self.AddMgnfield(mgnfield)

                mgncreat = _Mgncreat(fieldType=_Mgncreat.DECAPOLE, applicableRadius=0, xOffset=0, yOffset=0, mirrorSymmetry=0, sdum=mgnname)
                self.AddMgncreat(mgncreat)

                # increment mgn count
                self.flukamgncount += 1

            # book keeping information for the instance
            instance_bki['category']     = element.category
            instance_bki['outerRegion']  = flukaouterregion.name
            instance_bki['outerBody']    = flukaouterregion.zones[0].intersections[0].body.name  # TODO check if this is generally corrrect
            instance_bki['flukaRegions'] = [self.flukaregistry.PhysVolToRegionMap[pv.name]]
        # must be a fluka prototype
        else :

            # TODO should this be in creating the fluka custom method
            prototype_bki['category']     = element['prototype'].category
            prototype_bki['outerRegion']  = element['prototype']['customOuterRegion'].name
            prototype_bki['outerBody']    = element['prototype']['customOuterBodies'][0].name
            prototype_bki['flukaRegions'] = [r.name for r in element['prototype']['customRegions']]

            # create outer body in correct location
            outer_body = _copy.deepcopy(element['prototype']['customOuterBodies'][0])
            # rename outer_body
            outer_body.name = element.name.upper()
            outer_body = outer_body._transform(rotation, geomtranslation)
            outer_body._scale(0.1)

            # subtract from world
            zone = _pyg4.fluka.Zone()
            zone.addIntersection(outer_body)
            self.worldzone.addSubtraction(zone)

            # create region
            instance_region = _pyg4.fluka.Region(element.name.upper())
            zone = _pyg4.fluka.Zone()
            zone.addIntersection(outer_body)
            instance_region.addZone(zone)

            # add transformed lattice region body to fluka registry
            self.flukaregistry.addBody(outer_body)

            # add lattice region to fluka registry
            self.flukaregistry.addRegion(instance_region)

            instance_bki['outerBody'] = outer_body.name
            instance_bki['outerRegion'] = instance_region.name
            instance_bki['flukaRegions'] = [instance_region.name]
            instance_bki['rotation'] = rotation.tolist()
            instance_bki['translation'] = translation.tolist()
            instance_bki['geomtranslation'] = geomtranslation.tolist()

        # create transformation from prototype to instance
        trans_to_prototype   = prototype_bki['geomtranslation']
        trans_to_instance    = instance_bki['geomtranslation']
        rotation_to_instance = instance_bki['rotation'] # assumes prototypes in parking space is without rotation

        rotation    = _matrix2tbxyz(_np.linalg.inv(_np.array(rotation_to_instance)))

        rdi = _rotoTranslationFromTra2("TL"+format(self.flukalatcount, "03"),[[0,0,0], -_np.array(trans_to_instance)])
        rdi2 = _rotoTranslationFromTra2("TL"+format(self.flukalatcount, "03"),[rotation, [0,0,0]])
        rdi3 = _rotoTranslationFromTra2("TL"+format(self.flukalatcount, "03"),[[0,0,0], _np.array(trans_to_prototype)])
        rdi.extend(rdi2)
        rdi.extend(rdi3)
        self._GetFlukaRegistry(flukaRegistryAdd=True).addRotoTranslation(rdi)

        # create lattice card to link the two regions
        self.AddLattice(_Lattice(prototype_bki['outerBody'],instance_bki['outerRegion'], rotDefiName=rdi.name))

        # increment internal counter
        self.flukalatcount += 1


    def _GetGeant4Registry(self,geant4RegistryAdd = False) :
        """Internal helper for get geant4 registry."""
        if geant4RegistryAdd:
            if self.g4registry :
                g4registry = self.g4registry
            else :
                g4registry = _pyg4.geant4.Registry()
                self.g4registry = g4registry
        else:
            g4registry = _pyg4.geant4.Registry()

        return g4registry

    def _GetFlukaRegistry(self, flukaRegistryAdd = False) :
        """Internal helper for get fluka registry."""
        if flukaRegistryAdd :
            if self.flukaregistry :
                flukaregistry = self.flukaregistry
            else :
                flukaregistry = _pyg4.fluka.FlukaRegistry()
                self.flukaregistry = flukaregistry
        else :
            flukaregistry = _pyg4.fluka.FlukaRegistry()

        return flukaregistry

    def _ResetRegistries(self):
        """Internal helper for reset registries."""
        print("Resetting Fluka and Geant4 registries")
        self.flukaregistry = None
        self.g4registry = None

    def _MakeOffsetAndTiltTransforms(self, element, rotation, translation):
        """Internal helper for make offset and tilt transforms."""
        offsetX = element["offsetX"]
        offsetY = element["offsetY"]
        tilt    = element["tilt"]

        translation = translation + _np.array([offsetX, offsetY, 0])
        rotation =  rotation @ _tbxyz2matrix([0,0,tilt])

        return rotation, translation

    def _CalculateDipoleFieldStrength(self, momentum, rho):
        """Internal helper for calculate dipole field strength."""
        return 3.3356409519815204 * momentum / (rho / 1000.)

    def _CalculateQuadrupoleFieldStrength(self, momentum, k1):
        """Internal helper for calculate quadrupole field strength."""
        return 0

    def _AddBookkeepingTransformation(self, name, rotation, translation, geomtranslation = _np.array([0,0,0]), angle=0.0, k1=0.0):
        """Internal helper for add bookkeeping transformation."""
        self.elementBookkeeping[name]['rotation'] = rotation.tolist()
        self.elementBookkeeping[name]['translation'] = translation.tolist()
        self.elementBookkeeping[name]['geomtranslation'] = geomtranslation.tolist()
        self.elementBookkeeping[name]['angle'] = angle
        self.elementBookkeeping[name]['k1'] = k1

    def _AddBookkeepingUsrbin(self, usrbinnumber, usrbinname, rotation = None, translation = None):
        """Internal helper for add bookkeeping usrbin."""
        self.usrbinnumber_usrbininfo[usrbinnumber] = {"name":usrbinname, "rotation":rotation.tolist(), "translation":translation.tolist()}

    def _MakeFlukaComponentCommonG4(self, name, containerLV, containerPV, flukaConvert,
                                    rotation, translation, geomtranslation, category,
                                    convertMaterials = False,
                                    prototype = False):
        # convert materials
        """Internal helper for make fluka component common g4."""
        if convertMaterials:
            print("_MakeFlukaComponentCommon> convertMaterials")
            materialNameSet = containerLV.makeMaterialNameSet()
            self._MakeFlukaMaterials(list(materialNameSet))

        rotation = rotation @ _tbxyz2matrix(containerPV.rotation.eval())

        # convert geometry
        if flukaConvert:
            flukaouterregion, self.flukanamecount = _geant4PhysicalVolume2Fluka(containerPV,
                                                                                mtra=rotation,
                                                                                tra=geomtranslation,
                                                                                flukaRegistry=self.flukaregistry,
                                                                                flukaNameCount=self.flukanamecount,
                                                                                bakeTransforms=self.bakeTransforms)


            # cut volume out of mother zone
            for daughterzones in flukaouterregion.zones:
                if not prototype :
                    self.worldzone.addSubtraction(daughterzones)
                else :
                    self.parkingzone.addSubtraction(daughterzones)

        # make bookkeeping information
        if name not in self.elementBookkeeping :
            self.elementBookkeeping[name] = {}

        self.elementBookkeeping[name]['category'] = category

        # needed to book keep potentially deep lv-pv constructions in conversion
        physicalVolumeNames = containerLV.makeLogicalPhysicalNameSets()[1]
        physicalVolumeNames.add(containerPV.name)
        self.elementBookkeeping[name]['physicalVolumes'] = list(physicalVolumeNames)
        self.elementBookkeeping[name]['outerPhysicalVolume'] = containerPV.name
        self.elementBookkeeping[name]['outerRegion'] = flukaouterregion.name # TODO check if this is generally corrrect
        self.elementBookkeeping[name]['outerBody'] = flukaouterregion.zones[0].intersections[0].body.name # TODO check if this is generally corrrect

        try:
            self.elementBookkeeping[name]['flukaRegions'] = [self.flukaregistry.PhysVolToRegionMap[pv] for pv in
                                                             self.elementBookkeeping[name]['physicalVolumes']]
        except KeyError:
            pass

        # make transformed mesh for overlaps
        outerMesh = self._MakePlacedMesh(containerPV, rotation, geomtranslation)
        return {"placedmesh": outerMesh}

    def _MakeFlukaComponentCommonFluka(self, name, regionNames, category) :

        # make bookkeeping information
        """Internal helper for make fluka component common fluka."""
        if name not in self.elementBookkeeping :
            self.elementBookkeeping[name] = {}

        self.elementBookkeeping[name]['flukaRegions'] = regionNames
        self.elementBookkeeping[name]['category'] = category

    def _MakeGeant4GenericTrap(self, name,
                               length = 500, xhalfwidth = 50, yhalfwidth = 50,
                               e1=0, e2=0,
                               g4registry = None):

        """Internal helper for make geant4 generic trap."""
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

    def _MakePlacedMesh(self, physVol, rotation, translation):

        """Internal helper for make placed mesh."""
        mesh = physVol.logicalVolume.solid.mesh()

        aa = _tbxyz2axisangle(_matrix2tbxyz(rotation))
        mesh.rotate(aa[0], -aa[1] / _np.pi * 180.0)
        mesh.translate([translation[0], translation[1], translation[2]])

        return mesh

    def _MakeFlukaMaterials(self, materials = []):
        """Internal helper for make fluka materials."""
        for g4material in materials :
            if g4material not in self.flukaregistry.materialShortName :
                if type(g4material) is str :
                    g4material_name = g4material
                    g4material = _pyg4.geant4.nist_material_2geant4Material(g4material)
                    materialNameShort = "M" + format(self.flukaregistry.iMaterials, "03")
                    _geant4Material2Fluka(g4material,self.flukaregistry,materialNameShort=materialNameShort)
                    self.flukaregistry.materialShortName[g4material_name] = materialNameShort
                    self.flukaregistry.iMaterials += 1

# dynamic doc strings
Machine.AddDrift.__doc__ = """allowed kwargs: """ + \
                           " ".join(_Element._beampipe_allowed_keys) + \
                           " " + " ".join(_Element._outer_allowed_keys)
Machine.AddRBend.__doc__ = """allowed kwargs: """ + \
                           " ".join(_Element._beampipe_allowed_keys) + \
                           " " + " ".join(_Element._outer_allowed_keys) + \
                           " " + " ".join(_Element._rbend_allowed_keys) + \
                           " " + " ".join(_Element._tiltshift_allowed_keys)
Machine.AddSBend.__doc__ = """allowed kwargs: """ + \
                           " ".join(_Element._beampipe_allowed_keys) + \
                           " " + " ".join(_Element._outer_allowed_keys) + \
                           " " + " ".join(_Element._sbend_allowed_keys) + \
                           " " + " ".join(_Element._tiltshift_allowed_keys)
Machine.AddQuadrupole.__doc__ = """allowed kwargs """ + \
                                " ".join(_Element._beampipe_allowed_keys) + \
                                " " + " ".join(_Element._outer_allowed_keys) + \
                                " " + " ".join(_Element._quadrupole_allowed_keys) + \
                                " " + " ".join(_Element._tiltshift_allowed_keys)
Machine.AddSextupole.__doc__ = """allowed kwargs """ + \
                               " ".join(_Element._beampipe_allowed_keys) + \
                               " " + " ".join(_Element._outer_allowed_keys) + \
                               " " + " ".join(_Element._sextupole_allowed_keys) + \
                               " " + " ".join(_Element._tiltshift_allowed_keys)
Machine.AddOctupole.__doc__ = """allowed kwargs """ + \
                               " ".join(_Element._beampipe_allowed_keys) + \
                               " " + " ".join(_Element._outer_allowed_keys) + \
                               " " + " ".join(_Element._octupole_allowed_keys) + \
                               " " + " ".join(_Element._tiltshift_allowed_keys)
Machine.AddDecapole.__doc__ = """allowed kwargs """ + \
                               " ".join(_Element._beampipe_allowed_keys) + \
                               " " + " ".join(_Element._outer_allowed_keys) + \
                               " " + " ".join(_Element._decapole_allowed_keys) + \
                               " " + " ".join(_Element._tiltshift_allowed_keys)

Machine.AddTarget.__doc__ = """allowed kwargs""" \
                            " " + " ".join(_Element._outer_allowed_keys) + \
                            " " + " ".join(_Element._tiltshift_allowed_keys) + \
                            " " + " ".join(_Element._target_allowed_keys)
Machine.AddRCol.__doc__ = """allowed kwargs """ + \
                          " " + " ".join(_Element._outer_allowed_keys) + \
                          " " + " ".join(_Element._tiltshift_allowed_keys) + \
                          " " + " ".join(_Element._rcol_allowed_keys)
Machine.AddECol.__doc__ = """allowed kwargs """ + \
                          " " + " ".join(_Element._outer_allowed_keys) + \
                          " " + " ".join(_Element._tiltshift_allowed_keys) + \
                          " " + " ".join(_Element._ecol_allowed_keys)
Machine.AddJCol.__doc__ = """allowed kwargs """ + \
                          " " + " ".join(_Element._outer_allowed_keys) + \
                          " " + " ".join(_Element._tiltshift_allowed_keys) + \
                          " " + " ".join(_Element._jcol_allowed_keys)
Machine.AddShield.__doc__ = """allowed kwargs """ + \
                            " " + " ".join(_Element._outer_allowed_keys) + \
                            " " + " ".join(_Element._tiltshift_allowed_keys) + \
                            " " + " ".join(_Element._beampipe_allowed_keys) + \
                            " " + " ".join(_Element._shield_allowed_keys)
Machine.AddDump.__doc__ = """allowed kwargs """ + \
                          " " + " ".join(_Element._outer_allowed_keys) + \
                          " " + " ".join(_Element._tiltshift_allowed_keys) + \
                          " " + " ".join(_Element._dump_allowed_keys)
Machine.AddWireScanner.__doc__ = """allowed kwargs """ + \
                                 " " + " ".join(_Element._outer_allowed_keys) + \
                                 " " + " ".join(_Element._tiltshift_allowed_keys) + \
                                 " " + " ".join(_Element._beampipe_allowed_keys) + \
                                 " " + " ".join(_Element._wirescanner_allowed_keys)
Machine.AddGap.__doc__ = """allowed kwargs """ + \
                         " " + " ".join(_Element._outer_allowed_keys) + \
                         " " + " ".join(_Element._tiltshift_allowed_keys)

Machine.AddCustomG4.__doc__ = """allowed kwargs """ + \
                              " " + " ".join(_Element._customg4_allowed_keys)
Machine.AddCustomG4File.__doc__ = """allowed kwargs """ + \
                                  " " + " ".join(_Element._customg4file_allowed_keys)
Machine.AddSamplerPlane.__doc__ = """allowed kwargs: """ + \
                                  " ".join(_Element._sampler_plane_allowed_keys)
Machine.AddCustomFluka.__doc__ = """allowed kwargs: """ + \
                                 " ".join(_Element._customfluka_allowed_keys)
Machine.AddCustomFlukaFile.__doc__ = """allowed kwargs: """ + \
                                     " ".join(_Element._customflukafile_allowed_keys)
