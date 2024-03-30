import pyflubl as _pfbl

def test_T001_drift() :
    m = _pfbl.Builder.Machine()
    m.AddDrift(name="d1", length=1,
               beampipeMaterial = "G4_STAINLESS-STEEL",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.Write("T001_drift")

    return m

