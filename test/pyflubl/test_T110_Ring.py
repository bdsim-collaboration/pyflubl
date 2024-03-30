import pyflubl as _pfbl
import numpy as _np

def test_T110_Ring() :
    m = _pfbl.Builder.Machine()

    n = 20
    bendangle = 2.*_np.pi/n
    print(bendangle)
    for i in range(0,n,1):
        m.AddDrift(name="d1-"+str(i), length=0.5,
                   beampipeMaterial="G4_STAINLESS-STEEL",
                   beampipeRadius=30, beampipeThickness=5)
        m.AddSBend(name="rb_"+str(i), length=0.5, angle=bendangle)
        m.AddSamplerPlane(name="s1_"+str(i), length=1e-6, samplersize=1)

    m.Write("T110_Ring")

    return m