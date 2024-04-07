import pyflubl as _pfbl
import numpy as _np

def test_T111_Ring_SBend() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    n = 15
    bendangle = 2.*_np.pi/float(n)
    for i in range(0,n,1):
        m.AddDrift(name="d1-"+str(i), length=0.5,
                   beampipeMaterial="G4_STAINLESS-STEEL",
                   beampipeRadius=30, beampipeThickness=5)
        m.AddSBend(name="rb_"+str(i), length=0.5, angle=bendangle)
        m.AddQuadrupole(name="q_"+str(i), length=0.25, k1=0.5)
        m.AddSamplerPlane(name="s1_"+str(i), length=1e-6)

    m.Write("T111_Ring_SBend")

    return m