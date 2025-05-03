import pyflubl as _pfbl
import pyg4ometry as _pyg4
import numpy as _np

def test_T032_custom_G4() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(1,0,0,0,0,1)
    m.AddBeam(b)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(10)
    m.AddStart(s)

    # custom geometry
    g4registry = m._GetRegistry(True)
    outerMaterial = _pyg4.geant4.MaterialSingleElement("AIR",
                                                       atomic_number=1,
                                                       atomic_weight=1,
                                                       density=1)
    outersolid = _pyg4.geant4.solid.Tubs("custom_solid",0, 750, 1000, 0, _np.pi*2, g4registry)
    outerlogical = _pyg4.geant4.LogicalVolume(outersolid, outerMaterial, "custom_lv", g4registry)

    m.AddDrift(name="d1", length=1)
    m.AddSBend(name="b1", length=1, angle=_np.pi/6)
    m.AddDrift(name="d2", length=1)
    m.AddCustomG4(name="c1", length=1, customLV = outerlogical, convertMaterials=False)
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.Write("T032_Custom_G4")

def test_T032_custom_G4_File() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(1,0,0,0,0,1)
    m.AddBeam(b)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(10)
    m.AddStart(s)

    m.AddDrift(name="d1", length=1)
    m.AddSBend(name="b1", length=1, angle=_np.pi/6)
    m.AddDrift(name="d2", length=1)
    m.AddCustomG4File(name="c1", length=1, geometryFile="./geometryInput/test_T032_Custom_Pyg4.gdml", lvName="bl")
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.Write("T032_Custom_G4_File")

def test_T032_custom_Fluka() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(1,0,0,0,0,1)
    m.AddBeam(b)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(10)
    m.AddStart(s)

    # custom fluka geometry
    reader = _pyg4.fluka.Reader("./geometryInput/test_T032_Custom_Fluka_Gap.inp")
    registry = reader.getRegistry()

    outer_bodies = [registry.bodyDict[k] for k in ['outer']]
    regions = [registry.regionDict[k] for k in ['OUTER','SHIELD','BEAM','TARGET']]

    m.AddDrift(name="d1", length=1)
    m.AddSBend(name="b1", length=1, angle=_np.pi/8)
    m.AddDrift(name="d2", length=1)
    m.AddCustomFluka(name="c1", length=1,
                     customOuterBodies= outer_bodies,
                     customRegions = regions,
                     flukaRegistry= registry)
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddDrift(name="d3",length=1)
    m.AddSBendSplit(name="b2", length=2, angle=-_np.pi/8)
    m.AddDrift(name="d4", length=1)
    m.Write("T032_Custom_Fluka")

def test_T032_custom_Fluka_File() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(1,0,0,0,0,1)
    m.AddBeam(b)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(10)
    m.AddStart(s)

    # custom fluka geometry
    reader = _pyg4.fluka.Reader("./geometryInput/test_T032_Custom_Fluka_Gap.inp")
    registry = reader.getRegistry()

    outer_bodies = [registry.bodyDict[k] for k in ['outer']]
    regions = [registry.regionDict[k] for k in ['OUTER','SHIELD','BEAM','TARGET']]

    m.AddDrift(name="d1", length=1)
    m.AddSBend(name="b1", length=1, angle=_np.pi/8)
    m.AddDrift(name="d2", length=1)
    m.AddCustomFlukaFile(name="c1", length=1, geometryFile="./geometryInput/test_T032_Custom_Fluka_Gap.inp",
                         customOuterBodies="outer",
                         customRegions="OUTER SHIELD BEAM TARGET")
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddDrift(name="d3",length=1)
    m.AddSBendSplit(name="b2", length=2, angle=-_np.pi/8)
    m.AddDrift(name="d4", length=1)
    m.Write("T032_Custom_Fluka_File")

if __name__ == "__main__":
    test_T032_custom_G4()