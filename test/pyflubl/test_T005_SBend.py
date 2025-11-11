import pyflubl as _pfbl
import numpy as _np

def test_T005_sbend() :
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

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSBend(name="sb1", length=1, angle=_np.pi/8)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSBend(name="sb2", length=1, angle=_np.pi / 8)
    m.AddDrift(name="d3", length=1, beampipeMaterial = "TUNGSTEN")
    m.Write("T005_SBend")

def test_T005_sbend_tilt() :
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

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddSBend(name="sb1", length=1, angle=_np.pi/4, tilt=_np.pi/2)
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSBend(name="sb2", length=1, angle=_np.pi/4, tilt=_np.pi/2)
    m.AddDrift(name="d3", length=1, beampipeMaterial = "TUNGSTEN")

    m.Write("T005_SBend_tilt")

def test_T005_sbend_split() :
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

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddSBendSplit(name="sb1", length=2, angle=_np.pi/4, nsplit=10)
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSBendSplit(name="sb2", length=2, angle=-_np.pi/4, nsplit=10)

    m.Write("T005_SBend_Split")

def test_T005_sbend_split_tilt() :
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

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN")
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddSBendSplit(name="sb1", length=2, angle=_np.pi/4, tilt=_np.pi/2, nsplit=10)
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN")
    m.Write("T005_SBend_Split_tilt")

if __name__ == "__main__":
    test_T005_sbend()
    test_T005_sbend_tilt()
    test_T005_sbend_split()
    test_T005_sbend_split_tilt()