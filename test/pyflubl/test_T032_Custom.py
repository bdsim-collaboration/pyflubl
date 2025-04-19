import pyflubl as _pfbl
import pyg4ometry as _pyg4
import numpy as _np

def test_T032_custom_GDML() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(1,0,0,0,0,1)
    m.AddBeam(b)

    r = _pfbl.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Start(10)
    m.AddStart(s)

    # custom geometry
    g4registry = m._GetRegistry(True)
    outersolid = _pyg4.geant4.solid.Tubs("custom_solid",0, 750, 1000, 0, _np.pi*2, g4registry)
    outerlogical = _pyg4.geant4.LogicalVolume(outersolid, "G4_AIR", "custom_lv", g4registry)

    m.AddCustomGDML(name="c1", length=1, customlv = outerlogical)
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.Write("T032_Custom_GDML")

    return m

