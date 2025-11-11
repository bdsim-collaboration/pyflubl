import pyflubl as _pfbl
import numpy as _np

def make_T020_jcol() :
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
    m.AddJCol(name="jc1", length=1, horizontalWidth=200, xsize=25,
              material="IRON", outerMaterial="VACUUM")
    m.AddSamplerPlane(name="s1", length=1e-6)

    m.AddDrift(name="d2", length=1)
    m.AddJCol(name="jc2", length=1, horizontalWidth=200, xsize=25,
              material="IRON", outerMaterial="VACUUM", tilt=_np.pi/2)
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d3", length=1)

    m.AddDrift(name="d4", length=1)
    m.AddJCol(name="jc3", length=1, horizontalWidth=200, xsizeLeft=10, xsizeRight = 20,
              material="IRON", outerMaterial="VACUUM")
    m.AddSamplerPlane(name="s3", length=1e-6)
    m.AddDrift(name="d5", length=1)

    m.Write("T020_JCol")

    return m

def test_T020_jcol() :
    make_T020_jcol()

if __name__ == "__main__":
    test_T020_jcol()