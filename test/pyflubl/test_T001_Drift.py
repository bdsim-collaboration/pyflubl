import pyflubl as _pfbl

def test_T001_drift() :
    m = _pfbl.Builder.Machine(bakeTransforms=True)

    d = _pfbl.Fluka.Defaults('EM-CASCA')
    m.AddDefaults(d)

    # b = _pfbl.Fluka.Beam(energy=1, energySpread=0.01, particleType='ELECTRON')
    b = _pfbl.Fluka.Beam1(momentumOrKe=1, energySpread=0.01, sdum="ELECTRON")
    bp = _pfbl.Fluka.Beampos(xCentre=0, yCentre=0, zCentre=0, xCosine=0, yCosine=0)
    ba = _pfbl.Fluka.BeamAxes(xxCosine=1, xyCosine=0, xzCosine=0,
                              zxCosine=0, zyCosine=0, zzCosine=1)
    m.AddBeam1(b)
    m.AddBeampos(bp)
    m.AddBeamaxes(ba)

    r = _pfbl.Fluka.Randomiz()
    m.AddRandomiz(r)

    s = _pfbl.Fluka.Start(1000)
    m.AddStart(s)

    m.AddDrift(name="d1", length=1,
               vacuumMaterial="HYDROGEN",
               beampipeMaterial = "IRON",
               beampipeRadius=30, beampipeThickness=5)
    m.AddSamplerPlane(name="s1", length=1e-6)

    m.AddDrift(name="d2", length=1,
               vacuumMaterial="HELIUM",
               beampipeMaterial = "COPPER",
               beampipeRadius=50, beampipeThickness=10)

    m.AddDrift(name="d3", length=1,
               vacuumMaterial="NITROGEN",
               beampipeMaterial = "SILVER",
               beampipeRadius=100, beampipeThickness=20,
               outerMaterial="GOLD")


    m.Write("T001_Drift")

    return m

if __name__ == "__main__":
    test_T001_drift()