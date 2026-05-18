import pyflubl as _pfbl
import os as _os
import numpy as _np

def make_T001_drift() :
    '''Make a regular drift'''

    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.BuilderNew.Machine(bakeTransforms=True, verbose=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(momentumOrKe=1, energySpread=0.0, sdum="ELECTRON")
    bp = _pfbl.Fluka.Beampos(xCentre=0, yCentre=0, zCentre=-1e-5, xCosine=0, yCosine=0)
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
    m.AddDrift(name="d1", length=1,
               vacuumMaterial="VACUUM",
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5)
    m.AddSamplerPlane(name="s2",
                      length=1e-4)

    m.SaveJSON(this_dir+"/T001_Drift_coordinate.json")
    m.Write(this_dir+"/T001_Drift")

    return m

def make_T001_drift_many() :
    '''Make many regular drifts'''

    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.BuilderNew.Machine(bakeTransforms=True, verbose=True)

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
               vacuumMaterial="VACUUM",
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5)
    m.AddSamplerPlane(name="s1",
                      length=1e-4)

    m.AddDrift(name="d2", length=1,
               vacuumMaterial="VACUUM",
               beampipeMaterial = "IRON",
               beampipeRadius=50,
               beampipeThickness=10)
    m.AddSamplerPlane(name="s2",
                      length=1e-4)

    m.AddDrift(name="d3", length=1,
               vacuumMaterial="VACUUM",
               beampipeMaterial = "IRON",
               beampipeRadius=100,
               beampipeThickness=20,
               outerMaterial="AIR")
    m.AddSamplerPlane(name="s3",
                      length=1e-4)

    m.SaveJSON(this_dir + "/T001_Drift_many_coordinate.json")
    m.Write(this_dir+"/T001_Drift_many")

    return m

def make_T001_drift_cut_e() :
    '''Make a drift with poleface rotation'''

    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.BuilderNew.Machine(bakeTransforms=True, verbose=True)

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
               vacuumMaterial="VACUUM",
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5,
               outerE1=_np.pi/4, outerE2=_np.pi/4)

    m.SaveJSON(this_dir + "/T001_Drift_cut_e_coordinate.json")
    m.Write(this_dir+"/T001_Drift_cut_e")

    return m

def make_T001_drift_cut_e_p() :
    '''Make a drift with poleface rotation and tilt'''

    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.BuilderNew.Machine(bakeTransforms=True, verbose=True)

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
               vacuumMaterial="VACUUM",
               beampipeMaterial = "IRON",
               beampipeRadius=30,
               beampipeThickness=5,
               outerE1=_np.pi/4, outerP1=_np.pi/2,
               outerE2=_np.pi/4, outerP2=0)

    m.SaveJSON(this_dir + "/T001_Drift_cut_e_p_coordinate.json")
    m.Write(this_dir+"/T001_Drift_cut_e_p")

    return m

def test_T001_drift() :
    make_T001_drift()

def test_T001_drift_many() :
    make_T001_drift_many()

def test_T001_drift_cut_e() :
    make_T001_drift_cut_e()

def test_T001_drift_cut_e_p() :
    make_T001_drift_cut_e_p()

if __name__ == "__main__":
    test_T001_drift()
    test_T001_drift_many()
    test_T001_drift_cut_e()
    test_T001_drift_cut_e_p()