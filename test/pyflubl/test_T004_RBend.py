import pyflubl as _pfbl
import numpy as _np

def make_T004_rbend() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam1(momentumOrKe=1, energySpread=0.01, sdum="ELECTRON")
    bp = _pfbl.Fluka.Beampos(xCentre=0, yCentre=0, zCentre=0, xCosine=0, yCosine=0)
    ba = _pfbl.Fluka.BeamAxes(xxCosine=1, xyCosine=0, xzCosine=0,
                              zxCosine=0, zyCosine=0, zzCosine=1)
    m.AddBeam1(b)
    m.AddBeampos(bp)
    m.AddBeamaxes(ba)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(10)
    m.AddStart(s)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    #m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.AddRBend(name="rb1", length=1, angle=_np.pi/8, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddRBend(name="rb2", length=1, angle=_np.pi/8, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddDrift(name="d3", length=1, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.Write("T004_RBend")

    return m

def test_T004_rbend() :
    make_T004_rbend()

def make_T004_rbend_tilt() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam1(momentumOrKe=1, energySpread=0.01, sdum="ELECTRON")
    bp = _pfbl.Fluka.Beampos(xCentre=0, yCentre=0, zCentre=0, xCosine=0, yCosine=0)
    ba = _pfbl.Fluka.BeamAxes(xxCosine=1, xyCosine=0, xzCosine=0,
                              zxCosine=0, zyCosine=0, zzCosine=1)
    m.AddBeam1(b)
    m.AddBeampos(bp)
    m.AddBeamaxes(ba)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(10)
    m.AddStart(s)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    #m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.AddRBend(name="rb1", length=1, angle=_np.pi/8, tilt=_np.pi/2, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddRBend(name="rb2", length=1, angle=_np.pi/8, tilt=_np.pi/2, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddDrift(name="d3", length=1, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)

    m.Write("T004_RBend_tilt")

    return m

def test_T004_rbend_tilt() :
    make_T004_rbend_tilt()

if __name__ == "__main__":
    test_T004_rbend()