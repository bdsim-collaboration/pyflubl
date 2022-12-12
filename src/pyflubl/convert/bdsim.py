import numpy as _np
import pyg4ometry as _g4
import pybdsim as _bds
from .baseConverter import BaseConverter as _BaseConverter

class Bdsim(_BaseConverter) :
    def __init__(self, bdsimROOTFileName = None, bdsimGDMLFileName = None, addSamplers = True, samplerThickness = 1e-6, samplerSize=1000):
        # base class init
        super().__init__(samplerThickness,samplerSize)

        # derived class init
        self.bdsimROOTFileName = bdsimROOTFileName
        self.bdsimGDMLFileName = bdsimGDMLFileName
        self._load()
        self.addSamplers = addSamplers
        self.samplerThickness = samplerThickness

        self.g4registry = _g4.geant4.Registry()

    def _load(self):

        # load root and GDML files
        self.bdsimROOTFile = _bds.Data.Load(self.bdsimROOTFileName)
        self.bdsimGDMLFile = _g4.gdml.Reader(self.bdsimGDMLFileName)

    def toFluka(self):

        # materials
        self.flukaMachine.addMaterials(self.bdsimGDMLFile.getRegistry())

        # geometry model
        modelTree = self.bdsimROOTFile.GetModelTree()
        model     = self.bdsimROOTFile.GetModel().model
        modelTree.GetEntry(0)
        gdmlReg   = self.bdsimGDMLFile.getRegistry()

        for iele in range(0,model.n):

            #  Get position/rotation
            pos = model.midPos[iele]
            rot = model.midRot[iele]
            # print(pos,rot)

            pos    = [pos.X()*1000, pos.Y()*1000, pos.Z()*1000]
            rotMat = _np.matrix([[rot.XX(), rot.XY(), rot.XZ()],
                                 [rot.YX(), rot.YY(), rot.YZ()],
                                 [rot.ZX(), rot.ZY(), rot.ZZ()]])

            # Get PV/LV from GDML file
            pvName = model.pvNameWPointer[iele]
            pv = gdmlReg.physicalVolumeDict[pvName[0]]
            lv = pv.logicalVolume

            # Adapt lv to fit a sampler
            ext = lv.extent()
            dx = ext[1][0]-ext[0][0]
            dy = ext[1][1]-ext[0][1]
            dz = ext[1][2]-ext[0][2]

            clipBox = _g4.geant4.solid.Box(lv.name+"_newSolid",1.1*dx,1.1*dy,dz-1, self.g4registry, "mm")
            lv.replaceSolid(clipBox, rotation=[0,0,0], position=[0,0,0], punit="mm")
            clipBoxes = _g4.misc.NestedBoxes(lv.name+"_clipper", dx, dy, dz-1, self.g4registry, "mm", 5,5,5, lv.depth())
            lv.clipGeometry(clipBoxes, (0, 0, 0), (0, 0, 0))

            samplerPos = _np.array((_np.array(pos)+_np.dot(rotMat,_np.array([0,0,dz/2]))))[0]

            #print(iele, model.componentType[iele], model.componentName[iele], model.pvName[iele],pv.name, lv.name)
            print('element ',iele,type(pos),pos,type(rotMat),rotMat,type(samplerPos),samplerPos)
            print('-------------')
            # print(type(samplerPos),samplerPos)

            #v = _g4.visualisation.VtkViewer()
            #v.addLogicalVolume(lv
            #v.view(interactive=True)

            self.flukaMachine.placeElement(pos=pos,rot=rotMat,lv=lv)
            self.flukaMachine.placePlaneSampler(pos=samplerPos,rot=rotMat,samplerName="sampler_"+str(iele),material=self.bdsimGDMLFile.getRegistry().materialDict["G4_AIR0x7fca0e4b9020"])

        return self.flukaMachine










