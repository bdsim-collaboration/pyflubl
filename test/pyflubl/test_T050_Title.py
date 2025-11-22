import pyflubl as _pfbl
import os as _os

def make_T050_title() :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    t = _pfbl.Fluka.Title("TEST SIMULATION")
    m.AddTitle(t)

    b = _pfbl.Fluka.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(0,0,0,0,0,0)
    m.AddBeam(b)

    m.AddDrift(name="d1", length=1,
               beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s1", length=1e-6)

    m.Write(this_dir+"/T050_Title")

    return m

def test_T050_title() :
    make_T050_title()

if __name__ == "__main__":
    test_T050_title()