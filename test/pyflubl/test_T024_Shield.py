import pyflubl as _pfbl
import os as _os
import numpy as _np

def make_T024_Shield() :
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

    s = _pfbl.Fluka.Start(1)
    m.AddStart(s)

    uic = _pfbl.Fluka.Usricall()
    m.AddUsricall(uic)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    m.AddDrift(name="d1", length=1)
    m.AddShield(name="p1", length=0.25,
                outerMaterial="AIR",
                xsize=120,
                ysize=120,
                horizontalWidth=750,
                verticalWidth=750,
                outerHorizontalSize=1000,
                outerVerticalSize=1000)
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddDrift(name="d2", length=1)

    m.AddShield(name="p2", length=0.25,
                outerMaterial="AIR",
                xsize=120,
                ysize=120,
                horizontalWidth=750,
                verticalWidth=750,
                outerHorizontalSize=1000,
                outerVerticalSize=1000,
                tilt=_np.pi/4)
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d3", length=1)

    m.SaveJSON(this_dir + "/T024_Shield_coordinate.json")
    m.Write(this_dir+"/T024_Shield")

    return m

def test_T024_Shield() :
    make_T024_Shield()

if __name__ == "__main__":
    test_T024_Shield()