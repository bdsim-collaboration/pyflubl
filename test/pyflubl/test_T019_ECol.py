import pyflubl as _pfbl
import os as _os
import numpy as _np

def make_T019_ECol() :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.BuilderNew.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(momentumOrKe=1, energySpread=0, sdum="ELECTRON")
    bp = _pfbl.Fluka.Beampos(xCentre=0, yCentre=0, zCentre=0, xCosine=0, yCosine=0)
    ba = _pfbl.Fluka.BeamAxes(xxCosine=1, xyCosine=0, xzCosine=0,
                              zxCosine=0, zyCosine=0, zzCosine=1)

    m.AddBeam(b)
    m.AddBeampos(bp)
    m.AddBeamaxes(ba)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(1000)
    m.AddStart(s)

    uic = _pfbl.Fluka.Usricall()
    m.AddUsricall(uic)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    m.AddDrift(name="d1", length=1)
    m.AddECol(name="ec1", length=1, horizontalWidth=200, verticalWidth=200,
              xsize=50, ysize=100,
              material="IRON",
              outerMaterial="AIR")
    m.AddSamplerPlane(name="s1", length=1e-6)

    m.AddDrift(name="d2", length=1)
    m.AddECol(name="ec2", length=1, horizontalWidth=200, verticalWidth=200,
              xsize=100, ysize=50,
              material="IRON",
              outerMaterial="AIR")
    m.AddSamplerPlane(name="s2", length=1e-6)

    m.AddDrift(name="d3", length=1)
    m.AddECol(name="ec3", length=1, horizontalWidth=200, verticalWidth=200,
              xsize=0, ysize=0,
              material="IRON",
              outerMaterial="AIR")
    m.AddSamplerPlane(name="s3", length=1e-6)

    m.AddDrift(name="d4", length=1)
    m.AddECol(name="ec4", length=1, horizontalWidth=200, verticalWidth=200,
              xsize=50, ysize=100, tilt=_np.pi/4,
              material="IRON",
              outerMaterial="AIR")
    m.AddSamplerPlane(name="s4", length=1e-6)

    m.AddDrift(name="d5", length=1)

    m.SaveJSON(this_dir + "/T019_ECol_coordinate.json")
    m.Write(this_dir+"/T019_ECol")

    return m

def test_T019_ECol() :
    make_T019_ECol()

if __name__ == "__main__":
    test_T019_Ecol()