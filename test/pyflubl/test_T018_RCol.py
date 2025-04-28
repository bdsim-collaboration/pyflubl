import pyflubl as _pfbl

def test_T018_rcol() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(1,0,0,0,0,1)
    m.AddBeam(b)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(1000)
    m.AddStart(s)

    m.AddDrift(name="d1", length=1)
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddRCol(name="rc1", length=1, horizontalWidth=200, xsize=50, ysize=50,
              material="IRON", outerMaterial="VACUUM")
    m.AddDrift(name="d2", length=1)

    m.Write("T017_RCol")

    return m