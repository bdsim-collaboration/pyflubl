import pyflubl as _pfbl
import numpy as _np

def test_T100_Straight() :
    m = _pfbl.Builder.Machine()

    n = 5

    for i in range(0,n,1):
        m.AddDrift(name="d1_"+str(i), length=1,
                   beampipeMaterial="G4_STAINLESS-STEEL",
                   beampipeRadius=30, beampipeThickness=5)
        m.AddSamplerPlane(name="s1_"+str(i), length=1e-6, samplersize=1)

    m.Write("T100_Stright")

    return m