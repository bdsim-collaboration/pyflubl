import pyflubl as _pfbl
import numpy as _np

def test_T004_rbend() :
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

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    #m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.AddRBend(name="rb1", length=2, angle=_np.pi/4, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.Write("T004_RBend")

    return m
