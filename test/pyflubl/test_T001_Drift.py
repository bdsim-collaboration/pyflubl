import pyflubl as _pfbl

def test_T001_drift() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    b = _pfbl.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(0,0,0,0,0,0)

    m.AddBeam(b)

    m.AddDrift(name="d1", length=1,
               beampipeMaterial = "G4_STAINLESS-STEEL",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.Write("T001_Drift")

    return m

