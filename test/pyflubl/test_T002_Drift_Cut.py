import pyflubl as _pfbl
import numpy as _np

def test_T002_Drift_Cut() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)
    m.AddDrift(name="d1", length=1,
               beampipeMaterial = "G4_STAINLESS-STEEL",
               beampipeRadius=30, beampipeThickness=5,
               e1=_np.pi/4, e2=_np.pi/4)
    m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.Write("T002_Drift_Cut")

    return m

