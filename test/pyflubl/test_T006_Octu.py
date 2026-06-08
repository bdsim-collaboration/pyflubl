import pyflubl as _pfbl
import os as _os

def make_octu(tilt = 0, offsetX = 0, offsetY = 0, fileName = "T006_Octu"):
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

    s = _pfbl.Fluka.Start(100)
    m.AddStart(s)

    uic = _pfbl.Fluka.Usricall()
    m.AddUsricall(uic)

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    us = _pfbl.Fluka.Source(1, # type (1 - TWISS, 2 - SIGMA)
                            1e-9, 0, 1e-3, 0, 0, # x emit, alp, bet, eta, etap
                            1e-9, 0, 1e-3, 0, 0, # y emit, alp, bet, eta, etap
                            0, # energy spread
                            0, 0, 0, 0, 0, 0, # x0, xp0, y, yp0, t0, E0
                            sdum = "NONE")
    m.AddSource(us)

    m.AddDrift(name="d1", length=1)
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddOctupole(name="o1", length=0.25, k3=-2.5, tilt=tilt, offsetX=offsetX, offsetY=offsetY)
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddDrift(name="d2", length=1)

    m.SaveJSON(this_dir + "/" + fileName + "_coordinate.json")
    m.Write(this_dir + "/" + fileName)

    return m

def test_T006_octu() :
    make_octu(fileName="T006_Octu")
