import pyflubl as _pfbl
import os as _os

def make_T001_drift() :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    # b = _pfbl.Fluka.Beam(energy=1, energySpread=0.01, particleType='ELECTRON')
    b = _pfbl.Fluka.Beam1(momentumOrKe=1, energySpread=0.0, sdum="ELECTRON")
    bp = _pfbl.Fluka.Beampos(xCentre=0, yCentre=0, zCentre=0, xCosine=0, yCosine=0)
    ba = _pfbl.Fluka.BeamAxes(xxCosine=1, xyCosine=0, xzCosine=0,
                              zxCosine=0, zyCosine=0, zzCosine=1)
    m.AddBeam1(b)
    m.AddBeampos(bp)
    m.AddBeamaxes(ba)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(500)
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
    m.AddSamplerPlane(name="s2", length=1e-4)

    m.AddDrift(name="d3", length=1,
               vacuumMaterial="VACUUM",
               beampipeMaterial = "IRON",
               beampipeRadius=100,
               beampipeThickness=20,
               outerMaterial="AIR")
    m.AddSamplerPlane(name="s3", length=1e-4)

    m.Write(this_dir+"/T001_Drift")

    return m

def test_T001_drift() :
    make_T001_drift()

if __name__ == "__main__":
    test_T001_drift()