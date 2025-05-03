import pyflubl as _pfbl

def test_T023_shield() :
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
    m.AddShield(name="p2", length=0.25,
                outerMaterial="AIR",
                xsize=120,
                ysize=120,
                horizontalWidth=750,
                verticalWidth=750,
                outerHorizontalSize=1000,
                outerVerticalSize=1000
                )
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d2", length=1)
    m.Write("T023_shield")

    return m

if __name__ == "__main__":
    test_T023_shield()