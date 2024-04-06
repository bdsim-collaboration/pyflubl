import pyflubl as _pfbl
import numpy as _np

def test_T110_Ring_RBend() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    n = 4
    bendangle = 2.*_np.pi/n


    for i in range(0,n,1):
        m.AddDrift(name="d1-"+str(i), length=0.5,
                   beampipeMaterial="G4_STAINLESS-STEEL",
                   beampipeRadius=30, beampipeThickness=5)
        m.AddRBend(name="rb_"+str(i), length=0.5, angle=bendangle)
        # m.AddSamplerPlane(name="s1_"+str(i), length=1e-6)

    m.CheckModel()
    m.Write("T110_Ring_RBend")

    return m