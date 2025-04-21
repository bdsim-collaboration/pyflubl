import pyflubl as _pfbl
import numpy as _np

def test_T110_ring_rbend() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(1,0,0,0,0,1)
    m.AddBeam(b)

    r = _pfbl.Randomiz()
    m.AddRandomiz(r)

    ud = _pfbl.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    s = _pfbl.Start(10)
    m.AddStart(s)

    n = 5
    bendangle = 2.*_np.pi/n

    for i in range(0,n,1):
        m.AddDrift(name="d10-"+str(i), length=0.5,
                   beampipeMaterial="TUNGSTEN",
                   beampipeRadius=30, beampipeThickness=5)
        m.AddQuadrupole(name="q_"+str(i), length=0.25, k1=0.5)
        m.AddSamplerPlane(name="s1_"+str(i), length=1e-6)
        m.AddDrift(name="d11-"+str(i), length=0.5,
                   beampipeMaterial="TUNGSTEN",
                   beampipeRadius=30, beampipeThickness=5)
        m.AddRBend(name="rb_"+str(i), length=0.5, angle=bendangle)

    m.CheckModel()
    m.Write("T110_Ring_RBend")

    return m