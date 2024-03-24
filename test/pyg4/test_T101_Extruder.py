import pyflubl as _pfbl
import numpy as _np
import pyg4ometry as _pyg4
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.fluka as _flu
import pyg4ometry.visualisation as _vi
import pyg4ometry.convert as _con
import matplotlib.pyplot as _plt
from test_T100_Extrusion import test_T100_Extrusion  as _test_T100_Extrusion

def test_T101_Extruder(vis=False, interactive=False, fluka=True, writeNISTMaterials=True) :

    # g4 registry
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "1001", reg, True)
    wy = _gd.Constant("wy", "1001", reg, True)
    wz = _gd.Constant("wz", "1001", reg, True)

    [yokeCoordinates, coilCoordinates,
     beampipeInnerCoordinates, beampipeOuterCoordinates] =  _test_T100_Extrusion(vis=False)

    # materials
    if writeNISTMaterials:
        worldMaterial = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        yokeMaterial  = _g4.nist_material_2geant4Material("G4_Fe", reg)
        coilMaterial  = _g4.nist_material_2geant4Material("G4_Cu", reg)
        beampipeMaterial  = _g4.nist_material_2geant4Material("G4_Be", reg)
    else:
        worldMaterial = _g4.MaterialPredefined("G4_Galactic")
        yokeMaterial  = _g4.MaterialPredefined("G4_Fe")
        coilMaterial  = _g4.MaterialPredefined("G4_Cu", reg)
        beampipeMaterial  = _g4.MaterialPredefined("G4_Be", reg)


    worldSolid = _g4.solid.Box("worldSolid", wx, wy, wz, reg, "mm")
    es = _flu.Extruder("Magnet", length=400, registry=reg)

    r1 = es.addRegion("outer")
    es.setRegionMaterial("outer", worldMaterial)
    r1.append([-301, -301])
    r1.append([-301, 301])
    r1.append([301, 301])
    r1.append([301, -301])
    es.setRegionToOuterBoundary("outer")

    r2 = es.addRegion("yoke")
    es.setRegionMaterial("yoke", yokeMaterial)
    for p in yokeCoordinates :
        r2.append(p)

    r3 = es.addRegion("beampipe")
    es.setRegionMaterial("beampipe", yokeMaterial)
    for p in beampipeOuterCoordinates :
        r3.append([p[0]+75,p[1]])

    #r4 = es.addRegion("beampipeVacuum")
    #es.setRegionMaterial("beampipeVacuum", worldMaterial)
    #for p in beampipeInnerCoordinates :
    #    r4.append(p)

    r5 = es.addRegion("coil1")
    es.setRegionMaterial("coil1", coilMaterial)
    for p in coilCoordinates :
        r5.append([p[0]+25, p[1]+50])

    r6 = es.addRegion("coil2")
    es.setRegionMaterial("coil2", coilMaterial)
    for p in coilCoordinates :
        r6.append([p[0]+25, p[1]-50])

    r7 = es.addRegion("coil3")
    es.setRegionMaterial("coil3", coilMaterial)
    for p in coilCoordinates :
        r7.append([p[0]+125, p[1]+50])

    r8 = es.addRegion("coil4")
    es.setRegionMaterial("coil4", coilMaterial)
    for p in coilCoordinates :
        r8.append([p[0]+125, p[1]-50])

    es.buildCgalPolygons()
    es.buildGeant4Extrusions()

    # structure
    worldLogical = _g4.LogicalVolume(worldSolid, worldMaterial, "wl", reg)
    extruderLogical = _g4.LogicalVolume(es, worldMaterial, "extruderSolid", reg)
    extruderPhysical = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], extruderLogical, "extruderPhysical1", worldLogical, reg)

    reg.setWorld(worldLogical.name)

    if vis:
        v = _vi.VtkViewerColouredMaterialNew()
        v.addLogicalVolume(reg.getWorldVolume())
        v.buildPipelinesAppend()
        v.view(interactive=interactive)


    if fluka:
        freg = _con.geant4Reg2FlukaReg(reg)

        w = _flu.Writer()
        w.addDetector(freg)
        w.write("T101_Extruder.inp")

    return es