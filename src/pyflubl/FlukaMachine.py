import numpy as _np

import pyg4ometry.fluka as _fluka
import pyg4ometry.geant4.LogicalVolume as _LogicalVolume
import pyg4ometry.geant4.PhysicalVolume as _PhysicalVolume
import pyg4ometry.geant4.Registry as _Registry
import pyg4ometry.geant4.solid.Box as _Box

from pyg4ometry.convert.geant42Fluka import geant4PhysicalVolume2Fluka as _geant4PhysicalVolume2Fluka
from pyg4ometry.convert.geant42Fluka import geant4PhysicalVolume2Fluka as _geant4PhysicalVolume2Fluka
from pyg4ometry.convert.geant42Fluka import geant4MaterialDict2Fluka as _geant4MaterialDict2Fluka
from pyg4ometry.fluka.directive import rotoTranslationFromTra2 as _rotoTranslationFromTra2

class FlukaMachine :

    def __init__(self, useLattice = False, worldSize = (10000,10000,10000), storageSize=(100,100,100), storageLocation=(0,0,0)):

        # book keeping
        self.flukaNameCount = 0
        self.g4registry = _Registry() # needed for making PVs
        self.pvNameCount = {}

        # create fluka registry
        self.flukaRegistry = _fluka.FlukaRegistry()
        self.worldSize     = worldSize

        # if using lattice
        self.useLattice    = useLattice
        if self.useLattice:
            self.storageSize     = storageSize
            self.storageLocation = storageLocation
        else :
            self.storageSize = None
            self.storageLocation = None

        # create black body and world
        blackBody = _fluka.RPP("BLKBODY",
                               -2*worldSize[0]/10,2*worldSize[0]/10,
                               -2*worldSize[1]/10,2*worldSize[1]/10,
                               -2*worldSize[2]/10,2*worldSize[2]/10,
                               transform=_rotoTranslationFromTra2("BBROTDEF",[[0,0,0],[0,0,0]],
                                                                  flukaregistry=self.flukaRegistry),
                               flukaregistry=self.flukaRegistry)

        worldBody = _fluka.RPP("WORLD",
                               -worldSize[0]/10,worldSize[0]/10,
                               -worldSize[1]/10,worldSize[1]/10,
                               -worldSize[2]/10,worldSize[2]/10,
                               transform=_rotoTranslationFromTra2("BBROTDEF",[[0,0,0],[0,0,0]],
                                                                  flukaregistry=self.flukaRegistry),
                               flukaregistry=self.flukaRegistry)

        self.blackBodyZone = _fluka.Zone()
        self.worldZone     = _fluka.Zone()

        self.blackBodyZone.addIntersection(blackBody)
        self.blackBodyZone.addSubtraction(worldBody)

        self.worldZone.addIntersection(worldBody)

        self.blackBodyRegion = _fluka.Region("BLKHOLE")
        self.blackBodyRegion.addZone(self.blackBodyZone)
        self.flukaRegistry.addRegion(self.blackBodyRegion)

        self.worldRegion = _fluka.Region("WORLD")
        self.worldRegion.addZone(self.worldZone)
        self.flukaRegistry.addRegion(self.worldRegion)

    def addMaterials(self, g4reg):
        _geant4MaterialDict2Fluka(g4reg.materialDict, self.flukaRegistry)

    def placeElement(self, **kwargs):

        # check kwargs
        if len(kwargs) < 3 :
            print("FlukaMachine.placeElement need pos=[x,y,z], rot=[3x3] or [1x3], element=LV")
            return

        pos = kwargs['pos']
        rot = kwargs['rot']
        lv  = kwargs['lv']

        try :
            pvName = kwargs['name']
        except KeyError :
            pvName = lv.name+"_placement"

        print('placeElement',pvName,pos,rot)

        # fix LV cutting outer for sampler

        # add sampler

        # make a PV with the rotation and position

        pv = _PhysicalVolume([0,0,0],[0,0,0],lv,pvName,None,self.g4registry,addRegistry=False)

        # add to fluka registry
        flukaOuterRegion, self.flukaNameCount = _geant4PhysicalVolume2Fluka(pv,mtra=rot, tra=_np.array(pos),flukaRegistry=self.flukaRegistry,flukaNameCount=self.flukaNameCount)

        # cut volume out of mother zone
        for daughterZones in flukaOuterRegion.zones:
            self.worldZone.addSubtraction(daughterZones)

    def _placeElement_TBRot_LV(self, pos=[0,0,0], rot=[0,0,0], element = None):
        pass

    def _placeElement_MatRot_LV(self, pos=[0,0,0], rot=[[1,0,0],[0,1,0],[0,0,1]], element = None):
        pass

    def placePlaneSampler(self, pos=[0,0,0], rot=[[1,0,0],[0,1,0],[0,0,1]], samplerName = "sampler", samplerSize = 1000, samplerLength=1e-3,  material="G4_AIR"):


        # make box of correct size
        samplerSolid    = _Box(samplerName+"_solid",samplerSize,samplerSize,samplerLength,self.g4registry)
        samplerLogical  = _LogicalVolume(samplerSolid,material,samplerName+"_lv",self.g4registry)
        samplerPhysical = _PhysicalVolume([0,0,0],[0,0,0],samplerLogical,samplerName+"_pv",None)

        flukaOuterRegion, self.flukaNameCount = _geant4PhysicalVolume2Fluka(samplerPhysical,mtra=rot, tra=_np.array(pos),flukaRegistry=self.flukaRegistry,flukaNameCount=self.flukaNameCount)

        # cut volume out of mother zone
        for daughterZones in flukaOuterRegion.zones:
            self.worldZone.addSubtraction(daughterZones)

    def placeCylinderSampler(self, pos=[0,0,0], rot=[0,0,0], samplerRadius = 1000, samplerLength=1000, material="G4_Galactic"):
        pass

    def placeBoxSampler(self, pos=[0,0,0], rot=[0,0,0], material="G4_Galactic"):
        pass

    def exportINP(self, flukaINPFileName = "output.inp"):
        w = _fluka.Writer()
        w.addDetector(self.flukaRegistry)
        w.write(flukaINPFileName)

    def exportFLAIR(self):
        pass