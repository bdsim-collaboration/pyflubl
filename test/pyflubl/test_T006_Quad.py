import pyflubl as _pfbl
import numpy as _np

def quad_basic(tilt = 0, offsetX = 0, offsetY = 0, fileName = "T006_Quad"):
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(1,0,0,0,0,1)
    m.AddBeam(b)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(10)
    m.AddStart(s)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.AddQuadrupole(name="q1", length=0.5, k1=0.5, tilt=tilt, offsetX=offsetX, offsetY=offsetY)
    m.AddSamplerPlane(name="s2", length=1e-6, samplersize=1)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.Write(fileName)


def test_T006_quad() :
    quad_basic()

def test_T006_quad_tilt() :
    quad_basic(tilt=_np.pi/4, fileName="T006_Quad_tilt")

def test_T006_quad_offsetX() :
    quad_basic(offsetX=50, fileName="T006_Quad_offsetX")

def test_T006_quad_offsetY() :
    quad_basic(offsetY=50, fileName="T006_Quad_offsetY")