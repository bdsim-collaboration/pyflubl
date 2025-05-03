import pyflubl as _pfbl
import numpy as _np

def test_T111_ring_sbend() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    #b = _pfbl.Fluka.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    #b.AddBeamPosition(0,0,0,0,0)
    #b.AddBeamAxes(1,0,0,0,0,1)
    #m.AddBeam(b)

    b = _pfbl.Fluka.Beam1(momentumOrKe=1, energySpread=0.01, sdum="ELECTRON")
    bp = _pfbl.Fluka.Beampos(xCentre=0, yCentre=0, zCentre=0, xCosine=0, yCosine=0)
    ba = _pfbl.Fluka.BeamAxes(xxCosine=1, xyCosine=0, xzCosine=0,
                              zxCosine=0, zyCosine=0, zzCosine=1)
    m.AddBeam1(b)
    m.AddBeampos(bp)
    m.AddBeamaxes(ba)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    s = _pfbl.Fluka.Start(10)
    m.AddStart(s)

    n = 10
    bendangle = 2.*_np.pi/float(n)

    for i in range(0,n,1):
        m.AddDrift(name="d1-"+str(i), length=0.5,
                   beampipeMaterial="TUNGSTEN")
        m.AddSBendSplit(name="rb_"+str(i), length=0.5, angle=bendangle, nsplit=3)
        m.AddDrift(name="d2-"+str(i), length=0.5,
                   beampipeMaterial="TUNGSTEN")
        m.AddQuadrupole(name="q_"+str(i), length=0.25, k1=0.5)
        m.AddSamplerPlane(name="s1_"+str(i), length=1e-6)

    m.Write("T111_Ring_SBend")

    return m

if __name__ == "__main__":
    test_T111_ring_sbend()