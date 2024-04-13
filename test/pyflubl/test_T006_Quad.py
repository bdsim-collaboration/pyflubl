import pyflubl as _pfbl
import numpy as _np

def test_T006_Quad() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    b = _pfbl.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(0,0,0,0,0,0)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "G4_STAINLESS-STEEL",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.AddQuadrupole(name="q1", length=0.5, k1=0.5, tilt=_np.pi/4, offsetX=500, offsetY=500)
    m.AddSamplerPlane(name="s2", length=1e-6, samplersize=1)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "G4_STAINLESS-STEEL",
               beampipeRadius=30, beampipeThickness=5)
    m.Write("T006_Quad")

    return m
