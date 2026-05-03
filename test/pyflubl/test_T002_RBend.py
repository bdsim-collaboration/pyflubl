import pyflubl as _pfbl
import numpy as _np
import os as _os

def make_T002_RBend() :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.BuilderNew.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(momentumOrKe=1, energySpread=0.0, sdum="ELECTRON")
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

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    # set world material
    m.world_material = "VACUUM"

    m.AddDrift(name="d1",
               length=1,
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5,
               outerMaterial="AIR")
    m.AddRBend(name="rb1",
               length=1,
               angle=10/180*_np.pi,
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5)
    m.AddDrift(name="d2",
               length=1,
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5,
               outerMaterial="AIR")
    m.AddRBend(name="rb2",
               length=1,
               angle=-10/180*_np.pi,
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5)
    m.AddDrift(name="d3",
               length=1,
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5,
               outerMaterial="AIR")
    m.AddSamplerPlane(name="s1",
                      length=1e-4)

    m.SaveJSON(this_dir + "/T002_RBend_coordinate.json")
    m.Write(this_dir+"/T002_RBend")

    return m

def make_T002_RBend_tilt() :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.BuilderNew.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(momentumOrKe=1, energySpread=0.0, sdum="ELECTRON")
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

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    # set world material
    m.world_material = "VACUUM"

    m.AddDrift(name="d1", length=1,
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5,
               outerMaterial="AIR")
    # m.AddSamplerPlane(name="s1", length=1e-6, samplersize=1)
    m.AddRBend(name="rb1",
               length=1,
               angle=10/180*_np.pi,
               tilt=_np.pi/2,
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5)
    m.AddDrift(name="d2",
               length=1,
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5,
               outerMaterial="AIR")
    m.AddRBend(name="rb2",
               length=1,
               angle=-10/180*_np.pi,
               tilt=_np.pi/2,
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5)
    m.AddDrift(name="d3", length=1,
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5,
               outerMaterial="AIR")

    m.SaveJSON(this_dir + "/T002_RBend_tilt_coordinate.json")
    m.Write(this_dir+"/T002_RBend_tilt")

    return m

def make_T002_RBend_90deg() :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.BuilderNew.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(momentumOrKe=1, energySpread=0.0, sdum="ELECTRON")
    bp = _pfbl.Fluka.Beampos(xCentre=0, yCentre=0, zCentre=-1e-3, xCosine=0, yCosine=0)
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

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    # set world material
    m.world_material = "VACUUM"

    m.AddSamplerPlane(name="sstart",
                      length=1e-4)

    nrbend = 10
    for i in range(0,nrbend,1) :
        m.AddDrift("d"+str(i)+"_start", length=0.5)
        m.AddSamplerPlane(name="s"+str(i),
                          length=1e-4)
        m.AddDrift("d"+str(i)+"_end", length=0.5)

        m.AddRBend(name="rb"+str(i),
                        length=1,
                        angle=_np.pi/nrbend/2)


    m.SaveJSON(this_dir + "/T002_RBend_90deg_coordinate.json")
    m.Write(this_dir+"/T002_RBend_90deg")

    return m

def make_T002_RBend_90deg_tilt() :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.BuilderNew.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(momentumOrKe=1, energySpread=0.0, sdum="ELECTRON")
    bp = _pfbl.Fluka.Beampos(xCentre=0, yCentre=0, zCentre=-1e-3, xCosine=0, yCosine=0)
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

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    # set world material
    m.world_material = "VACUUM"

    m.AddSamplerPlane(name="sstart",
                      length=1e-4)

    nrbend = 10
    for i in range(0,nrbend,1) :
        m.AddDrift("d"+str(i)+"_start", length=0.5)
        m.AddSamplerPlane(name="s"+str(i),
                          length=1e-4)
        m.AddDrift("d"+str(i)+"_end", length=0.5)

        m.AddRBend(name="rb"+str(i),
                        length=1,
                        angle=_np.pi/nrbend/2,
                        tilt=_np.pi/2)


    m.SaveJSON(this_dir + "/T002_RBend_90deg_tilt_coordinate.json")
    m.Write(this_dir+"/T002_RBend_90deg_tilt")

    return m

def test_T002_RBend() :
    make_T002_RBend()

def test_T002_RBend_tilt() :
    make_T002_RBend_tilt()

def test_T002_RBend_90deg() :
    make_T002_RBend_90deg()

def test_T002_RBend_90deg_tilt() :
    make_T002_RBend_90deg_tilt()

if __name__ == "__main__":
    test_T002_RBend()
    test_T002_RBend_tilt()
    test_T002_RBend_90deg()
    test_T002_RBend_90deg_tilt()