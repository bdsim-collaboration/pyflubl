import pyflubl as _pfbl
import numpy as _np

def usrbin_basic() :
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

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

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

    return m

def test_T204_Usrbin() :

    m = usrbin_basic()

    ub1 = _pfbl.Fluka.Usrbin(binning=_pfbl.Fluka.Usrbin.CARTESIAN_STEP,
                             particle="ALL-PART",lun=-24,
                             xmax=100, ymax=100, zmax=1200, sdum="b1em",
                             xmin=-400, ymin=-100, zmin=-100,
                             nxbin=100, nybin=100, nzbin=100)
    m.AddUsrbin(ub1)

    ub2 = _pfbl.Fluka.Usrbin(binning=_pfbl.Fluka.Usrbin.CARTESIAN,
                             particle="ALL-PART",lun=-24,
                             xmax=10, ymax=10, zmax=120, sdum="b2em",
                             xmin=-10, ymin=-10, zmin=-10,
                             nxbin=100, nybin=100, nzbin=100)

    m.AddUsrbin(ub2)

    m.Write("T204_Usrbin")

    return m


def test_T204_Usrbin_element():

    m = usrbin_basic()

    eb1 = _pfbl.Fluka.Usrbin(binning=_pfbl.Fluka.Usrbin.CARTESIAN_STEP,
                             particle="ALL-PART",lun=-24,
                             xmax=50, ymax=50, zmax=50, sdum="eb1",
                             xmin=-50, ymin=-50, zmin=-50,
                             nxbin=101, nybin=101, nzbin=101)
    m.AddUsrbinToElement("d2", eb1)

    eb2 = _pfbl.Fluka.Usrbin(binning=_pfbl.Fluka.Usrbin.CARTESIAN_STEP,
                             particle="ALL-PART",lun=-24,
                             xmax=50, ymax=50, zmax=50, sdum="eb2",
                             xmin=-50, ymin=-50, zmin=-50,
                             nxbin=101, nybin=101, nzbin=101)
    m.AddUsrbinToElement("d4", eb2)

    m.Write("T204_Usrbin_element")

    return m


if __name__ == "__main__":
    test_T204_Usrbin()
