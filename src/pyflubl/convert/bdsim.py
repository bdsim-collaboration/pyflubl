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

            # Get PV/LV from GDML file
            pvName = model.pvNameWPointer[iele]
            pv = gdmlReg.physicalVolumeDict[pvName[0]]
            lv = pv.logicalVolume

            print(iele, model.componentType[iele], model.componentName[iele],
                  model.pvName[iele],pv.name, lv.name)

            self.flukaMachine.placeElement(pos=[0,0,0],rot=[0,0,0],lv=lv)

        return self.flukaMachine










