import pyflubl as _pfbl
import pyg4ometry as _pyg4
import numpy as _np

def test_IPAC_2025() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(1,0,0,0,0,1)
    m.AddBeam(b)

    r = _pfbl.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Start(10)
    m.AddStart(s)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSBendSplit(name="b1", length=1, angle=_np.pi/8)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSBendSplit(name="b2", length=1, angle=-_np.pi/8)
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddCustomFlukaFile(name="c1", length=1,
                         geometryFile="./geometryInput/test_T032_Custom_Fluka_Gap.inp",
                         outerBodies="outer",
                         regionNames="OUTER SHIELD BEAM TARGET")
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d3", length=0.5, beampipeMaterial = "TUNGSTEN")
    m.Write("IPAC_2025")

    return m