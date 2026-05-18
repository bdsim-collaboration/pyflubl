import pyflubl as _pfbl
import numpy as _np
import os as _os

def make_T003_SBend() :
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
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s1",
                      length=1e-4)
    m.AddSBend(name="sb1",
               length=1,
               angle=10/180*_np.pi)
    m.AddSamplerPlane(name="s2",
                      length=1e-4)
    m.AddDrift(name="d2",
               length=1,
               beampipeMaterial = "IRON",
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s3",
                      length=1e-4)
    m.AddSBend(name="sb2",
               length=1,
               angle=-10/180*_np.pi)
    m.AddSamplerPlane(name="s4",
                      length=1e-4)
    m.AddDrift(name="d3",
               length=1,
               beampipeMaterial = "IRON",
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s5",
                      length=1e-4)

    m.SaveJSON(this_dir + "/T003_SBend_coordinate.json")
    m.Write(this_dir+"/T003_SBend")

    return m

def make_T003_SBend_tilt() :
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
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s1",
                      length=1e-4)
    m.AddSBend(name="sb1",
               length=1,
               angle=_np.pi/18,
               tilt=_np.pi/2)
    m.AddSamplerPlane(name="s2",
                      length=1e-4)
    m.AddDrift(name="d2",
               length=1,
               beampipeMaterial = "IRON",
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s3",
                      length=1e-4)
    m.AddSBend(name="sb2",
               length=1,
               angle=-_np.pi/18,
               tilt=_np.pi/2)
    m.AddSamplerPlane(name="s4",
                      length=1e-4)
    m.AddDrift(name="d3",
               length=1,
               beampipeMaterial = "IRON")
    m.AddSamplerPlane(name="s5",
                      length=1e-4)

    m.SaveJSON(this_dir + "/T003_SBend_tilt_coordinate.json")
    m.Write(this_dir+"/T003_SBend_tilt")

    return m

def make_T003_SBend_split() :
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

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    m.AddDrift(name="d1",
               length=1,
               beampipeMaterial = "IRON",
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s1",
                      length=1e-4)
    m.AddSBendSplit(name="sb1",
                    length=1,
                    angle=_np.pi/18,
                    nsplit=10)
    m.AddSamplerPlane(name="s2",
                      length=1e-4)
    m.AddDrift(name="d2",
               length=1,
               beampipeMaterial = "IRON",
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s3",
                      length=1e-4)
    m.AddSBendSplit(name="sb2",
                    length=1,
                    angle=-_np.pi/18,
                    nsplit=10)
    m.AddSamplerPlane(name="s4",
                      length=1e-4)
    m.AddDrift(name="d3",
               length=1,
               beampipeMaterial = "IRON",
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s5",
                      length=1e-4)

    m.SaveJSON(this_dir + "/T003_SBend_split_coordinate.json")
    m.Write(this_dir+"/T003_SBend_split")

    return m

def make_T003_SBend_split_tilt() :
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
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s1",
                      length=1e-4)
    m.AddSBendSplit(name="sb1",
                    length=1,
                    angle=_np.pi/18,
                    tilt=_np.pi/2,
                    nsplit=10)
    m.AddSamplerPlane(name="s2",
                      length=1e-4)
    m.AddDrift(name="d2",
               length=1,
               beampipeMaterial = "IRON",
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s3",
                      length=1e-4)
    m.AddSBendSplit(name="sb2",
                    length=1,
                    angle=-_np.pi/18,
                    tilt=_np.pi/2,
                    nsplit=10)
    m.AddSamplerPlane(name="s4",
                      length=1e-4)
    m.AddDrift(name="d3",
               length=1,
               beampipeMaterial = "IRON",
               outerMaterial = "AIR")
    m.AddSamplerPlane(name="s5",
                      length=1e-4)

    m.SaveJSON(this_dir + "/T003_SBend_split_tilt_coordinate.json")
    m.Write(this_dir+"/T003_SBend_split_tilt")

    return m

def make_T003_SBend_split_90deg() :
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

    m.AddSamplerPlane(name="s1",
                      length=1e-4)
    m.AddSBendSplit(name="sb1",
                    length=7.853981633974483,
                    angle=_np.pi/2,
                    nsplit=50)
    m.AddSamplerPlane(name="s2",
                      length=1e-4)

    m.SaveJSON(this_dir + "/T003_SBend_split_90deg_coordinate.json")
    m.Write(this_dir+"/T003_SBend_split_90deg")

    return m

def test_T003_SBend() :
    make_T003_SBend()

def test_T003_SBend_tilt() :
    make_T003_SBend_tilt()

def test_T003_SBend_split() :
    make_T003_SBend_split()

def test_T003_SBend_split_tilt() :
    make_T003_SBend_split_tilt()

def test_T003_SBend_split_90deg() :
    make_T003_SBend_split_90deg()

if __name__ == "__main__":
    test_T003_SBend()
    test_T003_SBend_tilt()
    test_T003_SBend_split()
    test_T003_SBend_split_tilt()
    test_T003_SBend_split_90deg()
