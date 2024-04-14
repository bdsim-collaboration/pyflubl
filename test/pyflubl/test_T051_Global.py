import pyflubl as _pfbl

def test_T051_global() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Defaults('EM-CASCA')
    m.AddDefaults(d)

    g = _pfbl.Global(maxRegions = None, howAnalogue = None, dNear = None,
                     input = 3, inputGeometry = 1, memory = None)
    m.AddGlobal(g)

    b = _pfbl.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(0,0,0,0,0,0)
    m.AddBeam(b)

    m.AddDrift(name="d1", length=1,
               beampipeMaterial = "G4_STAINLESS-STEEL",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.Write("T051_Global")

    return m

