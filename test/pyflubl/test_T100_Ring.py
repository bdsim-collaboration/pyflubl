import pyflubl as _pfbl
import numpy as _np

def test_T100_ring() :
    m = _pfbl.Builder.Machine()

    n = 20
    bendangle = 2.*_np.pi/n
    print(bendangle)
    for i in range(0,n,1):
        m.AddDrift(name="d1_"+str(i), length=0.5)
        m.AddRBend(name="rb_"+str(i), length=0.5, angle=bendangle, bendxsize=0.75, bendysize=0.75)
        m.AddSamplerPlane(name="s1_"+str(i), length=1e-6, samplersize=1)

    m.Write("T100_ring")

    return m