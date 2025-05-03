import pyflubl as _pfbl
import numpy as _np

def test_T005_sbend() :
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

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN")
    #m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddSBend(name="sb1", length=0.2, angle=_np.pi/8)
    #m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN")
    m.Write("T005_SBend")

    return m

def test_T005_sbend_split() :
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

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddSBendSplit(name="sb1", length=2, angle=_np.pi/4, nsplit=10)
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN")
    m.Write("T005_SBend_Split")

    return m

if __name__ == "__main__":
    test_T005_sbend()