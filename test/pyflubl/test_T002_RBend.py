import pyflubl as _pfbl
import numpy as _np

def test_T002_rbend() :
    m = _pfbl.Builder.Machine()
    m.AddDrift(name="d1", length=1)
    m.AddRBend(name="rb1", length=1, angle=_np.pi/4, bendxsize=0.75, bendysize=0.75)
    m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.Write("T002_rbend")

    return m
