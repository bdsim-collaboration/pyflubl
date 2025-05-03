import pyflubl as _pfbl
import numpy as _np

def test_T100_straight() :
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

    n = 5
    for i in range(0,n,1):
        m.AddDrift(name="d1_"+str(i), length=1,
                   beampipeMaterial="TUNGSTEN",
                   beampipeRadius=30, beampipeThickness=5)
        m.AddSamplerPlane(name="s1_"+str(i), length=1e-6)

    m.Write("T100_Stright")

if __name__ == "__main__":
    test_T100_straight()