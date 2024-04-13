import pyflubl as _pfbl
import numpy as _np

def test_T002_Drift_Cut() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    b = _pfbl.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(0,0,0,0,0,0)

    m.AddDrift(name="d1", length=1,
               beampipeMaterial = "G4_STAINLESS-STEEL",
               beampipeRadius=30, beampipeThickness=5,
               e1=_np.pi/4, e2=_np.pi/4)
    m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.Write("T002_Drift_Cut")

    return m

