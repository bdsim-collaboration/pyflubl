import pyflubl as _pfbl
import os as _os

def make_T050_sampler() :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    b = _pfbl.Fluka.Beam(energy=1,energySpread=0.01,particleType='ELECTRON')
    b.AddBeamPosition(0,0,0,0,0)
    b.AddBeamAxes(1,0,0,0,0,1)
    m.AddBeam(b)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(1000)
    m.AddStart(s)

    m.AddDrift(name="d1", length=1,
               beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s1", length=1e-6, samplerDiameter=1000, samplerMaterial="HYDROGEN")

    m.AddDrift(name="d2", length=1,
               beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s2", length=1e-3, samplerDiameter=2000, samplerMaterial="HELIUM")

    m.AddDrift(name="d3", length=1,
               beampipeMaterial="TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s3", length=1e-2, samplerDiameter=3000, samplerMaterial="BERYLLIU")

    m.AddDrift(name="d4", length=1,
               beampipeMaterial = "TUNGSTEN",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s4", length=1e-1, samplerDiameter=4000, samplerMaterial="CARBON")

    m.Write(this_dir+"/T050_Sampler")

    return m

def test_T050_sampler() :
    make_T050_sampler()

if __name__ == "__main__":
    test_T050_sampler()