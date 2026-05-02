import pyflubl as _pfbl
import numpy as _np
import os as _os

def make_T270_Source() :
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

    s = _pfbl.Fluka.Start(10)
    m.AddStart(s)

    uic = _pfbl.Fluka.Usricall()
    m.AddUsricall(uic)

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    us = _pfbl.Fluka.Source(1, # type (1 - TWISS, 2 - SIGMA)
                            1e-6, 0, 1e-3, 0, 0, # x emit, alp, bet, eta, etap
                            1e-6, 0, 1e-3, 0, 0, # y emit, alp, bet, eta, etap
                            0, # energy spread
                            0, 0, 0, 0, 0, 0, # x0, xp0, y, yp0, t0, E0
                            sdum = "NONE")
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

    m.SaveJSON(this_dir + "/T270_Source_coordinate.json")
    m.Write(this_dir+"/T270_Source")

    return m

def test_T270_Source() :
    make_T270_Source()

if __name__ == "__main__":
    test_T270_Source()
