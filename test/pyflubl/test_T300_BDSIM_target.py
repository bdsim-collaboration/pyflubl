import pyflubl as _pfbl
import pybdsim as _pybd
import os as _os

def T300_BDSIM_target(material = "G4_Al", length = 1.0) :
    m = _pybd.Builder.Machine()

    m.AddDrift(name="d1", length=1.0)
    m.AddTarget(name="t", length=length, material=material)
    m.AddDrift(name="d2", length=1.0)

    b = _pybd.Beam.Beam()
    b.SetEnergy(1)
    m.AddBeam(b)

    o = _pybd.Options.Options()
    o.SetPhysicsList("em em_extra")
    m.AddOptions(o)

    m.Write("./T300_BDSIM_target_"+material+"_"+str(length))

def T300_FLUKA_target(material = "ALUMINUM", length = 1.0) :

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

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    ud = _pfbl.Fluka.Userdump(mgdraw=100, lun=23, mgdrawOption=-1, userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    m.AddDrift(name="d1", length=1, beampipeMaterial="VACUUM")
    m.AddSamplerPlane(name="d1s", length=1e-6)

    m.AddTarget(name="t1", length=length, material=material)
    m.AddSamplerPlane(name="t1s", length=1e-6)

    m.AddDrift(name="d2", length=1, beampipeMaterial="VACUUM")
    m.AddSamplerPlane(name="d2s", length=1e-6)

    m.SaveJSON(this_dir + "/T300_FLUKA_target_"+material+"_"+str(length)+"_coordinates.json")
    m.Write(this_dir + "/T300_FLUKA_target_"+material+"_"+str(length))

def test_T300_BDSIM_target_Al_001cm() :
    T300_FLUKA_target(material="ALUMINUM", length=0.01)
    T300_BDSIM_target(material="G4_Al", length=0.01)

def test_T300_BDSIM_target_Al_010cm() :
    T300_FLUKA_target(material="ALUMINUM", length=0.1)
    T300_BDSIM_target(material="G4_Al", length=0.1)

def test_T300_BDSIM_target_Al_025cm() :
    T300_FLUKA_target(material="ALUMINUM", length=0.25)
    T300_BDSIM_target(material="G4_Al", length=0.5)

def test_T300_BDSIM_target_Al_050cm() :
    T300_FLUKA_target(material="ALUMINUM", length=0.5)
    T300_BDSIM_target(material="G4_Al", length=0.5)

def test_T300_BDSIM_target_Al_100cm() :
    T300_FLUKA_target(material="ALUMINUM", length=1.0)
    T300_BDSIM_target(material="G4_Al", length=1.0)

