import pyg4ometry as _g4
import pybdsim as _bds

class Bdsim :
    def __init__(self, bdsimROOTFileName = None, bdsimGDMLFileName = None, addSamplers = True, samplerThickness = 1e-7):
        self.bdsimROOTFileName = bdsimROOTFileName
        self.bdsimGDMLFileName = bdsimGDMLFileName
        self._load()
        self.addSamplers = addSamplers
        self.samplerThickness = samplerThickness
        self.flukaReg = _g4.fluka.FlukaRegistry()

    def _load(self):
        self.bdsimROOTFile = _bds.Data.Load(self.bdsimROOTFileName)
        self.bdsimGDMLFile = _g4.gdml.Reader(self.bdsimGDMLFileName)

    def toFluka(self):

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

        return model










