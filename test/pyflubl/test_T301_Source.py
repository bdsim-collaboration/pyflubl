import pyflubl as _pfbl
import numpy as _np

def test_T301_Source() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam1(momentumOrKe=1, energySpread=0.1, sdum="ELECTRON")
    bp = _pfbl.Fluka.Beampos(xCentre=0, yCentre=0, zCentre=0, xCosine=0, yCosine=0)
    ba = _pfbl.Fluka.BeamAxes(xxCosine=1, xyCosine=0, xzCosine=0,
                              zxCosine=0, zyCosine=0, zzCosine=1)
    m.AddBeam1(b)
    m.AddBeampos(bp)
    m.AddBeamaxes(ba)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(1000)
    m.AddStart(s)

    uic = _pfbl.Fluka.Usricall()
    m.AddUsricall(uic)

    us = _pfbl.Fluka.Source()
    m.AddSource(us)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddSBendSplit(name="sb1", length=2, angle=_np.pi/4, nsplit=10)
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSBendSplit(name="sb2", length=2, angle=-_np.pi/4, nsplit=10)
    m.AddSamplerPlane(name="s3", length=1e-6)
    m.AddDrift(name="d3", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSBendSplit(name="sb3", length=2, angle=-_np.pi/4, nsplit=10)
    m.AddSamplerPlane(name="s4", length=1e-6)
    m.AddDrift(name="d4", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSBendSplit(name="sb4", length=2, angle=_np.pi/4, nsplit=10)
    m.AddSamplerPlane(name="s5", length=1e-6)
    m.AddDrift(name="d5", length=1, beampipeMaterial = "TUNGSTEN")

    m.Write("T301_Source")
    return m

if __name__ == "__main__":
    test_T301_Source()
