import pyflubl as _pfbl
import numpy as _np
import pyg4ometry as _pyg4
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.visualisation as _vi
import matplotlib.pyplot as _plt
import os as _os

def make_T100_Extrusion(vis = False, writeNISTMaterials=True) :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    # g4 registry
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "301", reg, True)
    wy = _gd.Constant("wy", "301", reg, True)
    wz = _gd.Constant("wz", "401", reg, True)

    # yoke
    yokeCoordindates = []
    yokeCoordindates.append([-100,-125])
    yokeCoordindates.append([-100,125])
    yokeCoordindates.append([100,125])
    yokeCoordindates.append([100,25])
    yokeCoordindates.append([50,25])
    yokeCoordindates.append([50,75])
    yokeCoordindates.append([-50,75])
    yokeCoordindates.append([-50,-75])
    yokeCoordindates.append([ 50,-75])
    yokeCoordindates.append([ 50,-25])
    yokeCoordindates.append([100,-25])
    yokeCoordindates.append([100,-125])
    yokeSlices = [[-200, [0, 0], 1], [200, [0, 0], 1]]

    # coil
    coilCoordinates = []
    coilCoordinates.append([-20,-20])
    coilCoordinates.append([-20,20])
    coilCoordinates.append([20,20])
    coilCoordinates.append([20,-20])
    coilSlices = [[-200, [0, 0], 1], [200, [0, 0], 1]]

    # beam pipe
    beampipeOuterCoordinates = []
    beampipeOuterCoordinates.append([-40,-20])
    beampipeOuterCoordinates.append([-40,20])
    beampipeOuterCoordinates.append([40,20])
    beampipeOuterCoordinates.append([40,-20])

    beampipeInnerCoordinates = []
    beampipeInnerCoordinates.append([-38,-18])
    beampipeInnerCoordinates.append([-38,18])
    beampipeInnerCoordinates.append([38,18])
    beampipeInnerCoordinates.append([38,-18])

    beampipeSlices = [[-200, [0, 0], 1], [200, [0, 0], 1]]


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

    # solids
    worldSolid = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    yokeSolid  = _g4.solid.ExtrudedSolid("yokeSolid", yokeCoordindates, yokeSlices, reg, "mm")
    coilSolid  = _g4.solid.ExtrudedSolid("coilSolid", coilCoordinates, coilSlices, reg, "mm")
    beampipeOuterSolid    = _g4.solid.ExtrudedSolid("beampipeOuterSolid",beampipeOuterCoordinates, beampipeSlices, reg, "mm")
    beampipeInnerSolid    = _g4.solid.ExtrudedSolid("beampipeInnerSolid",beampipeInnerCoordinates, beampipeSlices, reg, "mm")
    beampipeSolid = _g4.solid.Subtraction("beampipeSolid",beampipeOuterSolid,beampipeInnerSolid,[[0,0,0],[0,0,0]],reg)

    worldSolid      = _g4.solid.Box("worldSolid", wx, wy, wz, reg, "mm")
    worldLogical    = _g4.LogicalVolume(worldSolid, worldMaterial, "worldLogical", reg)
    yokeLogical     = _g4.LogicalVolume(yokeSolid, yokeMaterial, "yokeLogical", reg)
    coilLogical     = _g4.LogicalVolume(coilSolid, coilMaterial, "coilLogical", reg)
    beampipeLogical = _g4.LogicalVolume(beampipeSolid, beampipeMaterial, "beampipeLogical", reg)
    yokePhysical = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], yokeLogical, "yokePhysical_1", worldLogical, reg)
    coilPhysical1 = _g4.PhysicalVolume([0, 0, 0],[25, 50, 0], coilLogical, "coilPhysical_1", worldLogical, reg)
    coilPhysical2 = _g4.PhysicalVolume([0, 0, 0], [25, -50, 0], coilLogical, "coilPhysical_2", worldLogical, reg)
    coilPhysical3 = _g4.PhysicalVolume([0, 0, 0], [125, 50, 0], coilLogical, "coilPhysical_3", worldLogical, reg)
    coilPhysical4 = _g4.PhysicalVolume([0, 0, 0], [125, -50, 0], coilLogical, "coilPhysical_4", worldLogical, reg)
    beampipePhysical = _g4.PhysicalVolume([0, 0, 0], [75, 0, 0], beampipeLogical, "beampipePhysical", worldLogical, reg)

    # set world volume
    reg.setWorld(worldLogical.name)

    if vis :
        v = _vi.VtkViewerColouredMaterialNew()
        v.addLogicalVolume(reg.getWorldVolume())
        v.buildPipelinesAppend()
        v.view(interactive=True)

    freg = _pyg4.convert.geant4Reg2FlukaReg(reg)
    flukafilename = "T100_Extrusion.inp"
    w = _pyg4.fluka.Writer()
    w.addDetector(freg)
    w.write(this_dir+"/"+flukafilename)

    return [yokeCoordindates, coilCoordinates, beampipeInnerCoordinates, beampipeOuterCoordinates]

def test_T100_Extrusion(vis = False, writeNISTMaterials=True) :
    make_T100_Extrusion(vis, writeNISTMaterials)




