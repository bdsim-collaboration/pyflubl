import pyflubl as _pfbl

def make_T024_dump() :
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
    m.AddDump(name="p1", length=1, horizontalWidth=200,
              outerMaterial="VACUUM")
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddDrift(name="d2", length=1)
    m.AddDump(name="p2", length=1, horizontalWidth=200,
              outerMaterial="VACUUM", apertureType="circular")
    m.AddSamplerPlane(name="s2", length=1e-6)

    m.Write("T024_dump")

    return m

def test_T024_dump() :
    make_T024_dump()

if __name__ == "__main__":
    test_T024_dump()