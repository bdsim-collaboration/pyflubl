import numpy as _np
import pyg4ometry as _g4
import pybdsim as _bds
from .baseConverter import BaseConverter as _BaseConverter

class Bdsim(_BaseConverter) :
    def __init__(self, bdsimROOTFileName = None, bdsimGDMLFileName = None,
                 addSamplers = True, samplerThickness = 1e-6, samplerSize=1000,
                 bdsimGMADFileName = ""):
        # base class init
        super().__init__(samplerThickness,samplerSize)

        # derived class init
        self.bdsimROOTFileName = bdsimROOTFileName
        self.bdsimGDMLFileName = bdsimGDMLFileName
        self.bdsimGMADFileName = bdsimGMADFileName

        self._load()
        self.addSamplers = addSamplers
        self.samplerThickness = samplerThickness

        self.g4registry = _g4.geant4.Registry()

        self.samplerRegionNames = []

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

        samplerMaterial = gdmlReg.findMaterialByName("G4_AIR")[0]

        # other information required for flukaBdsim
        self.flukaMachine.conversionData = {}
        self.flukaMachine.conversionData['bdsimROOTFileName'] = self.bdsimROOTFileName
        self.flukaMachine.conversionData['bdsimGDMLFileName'] = self.bdsimGDMLFileName
        self.flukaMachine.conversionData['bdsimGMADFileName'] = self.bdsimGMADFileName
        self.flukaMachine.conversionData['addSamplers']       = self.addSamplers
        self.flukaMachine.conversionData['samplerThickness']  = self.samplerThickness
        self.flukaMachine.conversionData['samplerSize']       = self.samplerSize

        for iele in range(0,model.n):

            #  Get position/rotation
            pos = model.midPos[iele]
            rot = model.midRot[iele]
            rotEnd = model.endRot[iele]

            if iele != model.n-1 :
                rotNext = model.endRot[iele+1]
            else :
                rotNext = rot

            # convert from ROOT root to np arrays
            pos    = [pos.X()*1000, pos.Y()*1000, pos.Z()*1000] # pyg4ometry in mm and BDSIM output in m
            rotMat = _np.matrix([[rot.XX(), rot.XY(), rot.XZ()],
                                 [rot.YX(), rot.YY(), rot.YZ()],
                                 [rot.ZX(), rot.ZY(), rot.ZZ()]])
            rotEndMat = _np.matrix([[rotEnd.XX(), rotEnd.XY(), rotEnd.XZ()],
                                    [rotEnd.YX(), rotEnd.YY(), rotEnd.YZ()],
                                    [rotEnd.ZX(), rotEnd.ZY(), rotEnd.ZZ()]])
            rotNextMat = _np.matrix([[rotNext.XX(), rotNext.XY(), rotNext.XZ()],
                                     [rotNext.YX(), rotNext.YY(), rotNext.YZ()],
                                     [rotNext.ZX(), rotNext.ZY(), rotNext.ZZ()]])

            # Get PV/LV from GDML file
            pvName = model.pvNameWPointer[iele]
            pv = gdmlReg.physicalVolumeDict[pvName[0]]
            lv = pv.logicalVolume

            # Adapt lv to fit a sampler
            ext = lv.extent()
            dx = ext[1][0]-ext[0][0]
            dy = ext[1][1]-ext[0][1]
            dz = ext[1][2]-ext[0][2]

            #clipBox = _g4.geant4.solid.Box(lv.name+"_newSolid"+str(iele),1.1*dx,1.1*dy,dz-1, self.g4registry, "mm")
            #lv.replaceSolid(clipBox, rotation=[0,0,0], position=[0,0,0], punit="mm")
            #clipBoxes = _g4.misc.NestedBoxes(lv.name+"_clipper", dx, dy, dz-1, self.g4registry, "mm", 5,5,0, lv.depth())
            #lv.clipGeometry(clipBoxes, (0, 0, 0), (0, 0, 0))

            samplerPos = _np.array((_np.array(pos)+_np.dot(rotMat,_np.array([0,0,dz/2]))))[0]

            print('bdsim.toFluka> element type={} name={} iele={} pos={} rot={} samplerPos={}'.format(model.componentType[iele],model.componentName[iele],
                                                                                                      iele,pos,rotMat.flatten(),samplerPos))

            self.flukaMachine.placeElement(pos=pos,rot=rotMat,lv=lv)

            #psName = self.flukaMachine.placePlaneSampler(pos=samplerPos,
            #                                             rot=rotEndMat,
            #                                             samplerName="sampler_"+str(iele),
            #                                             material=samplerMaterial)
            #self.samplerRegionNames.append(psName)

            #psName = self.flukaMachine.placeCylinderSampler(pos=pos,
            #                                                rot=rotEndMat,
            #                                                samplerName="samplerCylinder_"+str(iele),
            #                                                samplerLength=dz,
            #                                                samplerRadius=max(dx,dy)*1.01,
            #                                                material=samplerMaterial)
            #self.samplerRegionNames.append(psName)

            #psName = self.flukaMachine.placeSphereSampler(pos=pos,
            #                                              rot=rotEndMat,
            #                                              samplerName="samplerSphere_"+str(iele),
            #                                              samplerRadius=1000,
            #                                              material=samplerMaterial)
            #self.samplerRegionNames.append(psName)

        return self.flukaMachine










