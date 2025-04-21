import pyflubl as _pfbl
import numpy as _np

def test_T002_drift_cut() :
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

    m.AddDrift(name="d1", length=1,
               beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5,
               e1=_np.pi/4, e2=_np.pi/4)
    m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.Write("T002_Drift_Cut")

    return m

