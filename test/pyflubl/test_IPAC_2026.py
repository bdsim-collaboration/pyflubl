import pyflubl as _pfbl
import pyg4ometry as _pyg4
import os as _os
import numpy as _np

def IPAC_2026_Lattice() :

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

    s = _pfbl.Fluka.Start(10)
    m.AddStart(s)

    uic = _pfbl.Fluka.Usricall()
    m.AddUsricall(uic)

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    d1 = m.AddDrift(name="d1", length=1, add=False)
    m.AddLatticePrototype(d1)
    m.AddLatticeInstance("d1i1","d1")
    m.AddLatticeInstance("d1i2","d1")
    m.AddLatticeInstance("d1i3","d1")

    m.Write(this_dir + "/IPAC_2026_Lattice")

def IPAC_2026() :

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

    us = _pfbl.Fluka.Source(1,  # type (1 - TWISS, 2 - SIGMA)
                            1e-10, 0, 1e-4, 0, 0,  # x emit, alp, bet, eta, etap
                            1e-10, 0, 1e-4, 0, 0,  # y emit, alp, bet, eta, etap
                            0,  # energy spread
                            0, 0, 0, 0, 0, 0,  # x0, xp0, y, yp0, t0, E0
                            sdum="NONE")
    m.AddSource(us)

    # Make materials (SS 316 )
    fr = m._GetFlukaRegistry(True)
    fm_c = _pyg4.fluka.Material("C", 6, 2.266, 12, flukaregistry=fr)  # graphite density
    fm_mn = _pyg4.fluka.Material("MN", 25, 7.21, 56, flukaregistry=fr)  # density range 7.21 - 7.47 g/cm^3
    fm_p = _pyg4.fluka.Material("P", 15, 1.82, 31, flukaregistry=fr)  # white 1.82 g/cm^3
    fm_s = _pyg4.fluka.Material("S", 16, 2.07, 32, flukaregistry=fr)
    fm_si = _pyg4.fluka.Material("SI", 14, 2.33, 28, flukaregistry=fr)
    fm_cr = _pyg4.fluka.Material("CR", 24, 7.19, 52, flukaregistry=fr)
    fm_ni = _pyg4.fluka.Material("NI", 28, 8.90, 58, flukaregistry=fr)
    fm_mo = _pyg4.fluka.Material("MO", 42, 10.22, 96, flukaregistry=fr)
    fm_fe = _pyg4.fluka.Material("FE", 26, 7.874, 56, flukaregistry=fr)
    fm_ss = _pyg4.fluka.Compound("SS", 8.0, [(fm_c, 0.08 / 100),
                                             (fm_mn, 2 / 100),
                                             (fm_p, 0.045 / 100),
                                             (fm_s, 0.03 / 100),
                                             (fm_si, 1 / 100),
                                             (fm_cr, 16 / 100),
                                             (fm_ni, 10 / 100),
                                             (fm_mo, 2 / 100),
                                             (fm_fe, 68.845 / 100)],
                                 "mass",
                                 flukaregistry=fr)

    m.AddDrift(name="d1", length=1, beampipeMaterial="IRON")
    m.AddSamplerPlane(name="s1", length=1e-6)
    m.AddQuadrupole(name="q1", length=0.25, k1=-0.2, beampipeMaterial="IRON")
    m.AddDrift(name="d2", length=1.0, beampipeMaterial="IRON")
    m.AddSamplerPlane(name="s2", length=1e-6)
    m.AddTarget(name="t1", length=0.01, material="IRON")
    m.AddSamplerPlane(name="s3", length=1e-6)
    m.AddDrift(name="d3", length=1.0, beampipeMaterial="IRON")
    m.AddSamplerPlane(name="s4", length=1e-6)
    m.AddSBendSplit(name="sb1", length=2, angle=_np.pi / 4, nsplit=10, beampipeMaterial="IRON")
    # m.AddDrift(name="sb1", length=2.0, beampipeMaterial="IRON")
    m.AddSamplerPlane(name="s5", length=1e-6)
    m.AddDrift(name="d4", length=1.0, beampipeMaterial="IRON")
    m.AddSamplerPlane(name="s6", length=1e-6)

    eb1 = _pfbl.Fluka.Usrbin(binning=_pfbl.Fluka.Usrbin.CARTESIAN_STEP,
                             particle="ALL-PART",lun=-24,
                             xmax=50, ymax=50, zmax=50, sdum="eb1",
                             xmin=-50, ymin=-50, zmin=-50,
                             nxbin=101, nybin=101, nzbin=101)
    m.AddUsrbinToElement("t1", eb1)


    eb2 = _pfbl.Fluka.Usrbin(binning=_pfbl.Fluka.Usrbin.CARTESIAN_STEP,
                             particle="ALL-PART",lun=-24,
                             xmax=50, ymax=50, zmax=150, sdum="eb2",
                             xmin=-50, ymin=-50, zmin=-150,
                             nxbin=101, nybin=101, nzbin=101)
    m.AddUsrbinToElement("d4", eb2)

    m.SaveJSON(this_dir + "/IPAC_2026_coordinate.json")
    m.Write(this_dir + "/IPAC_2026")

def test_IPAC_2026():
    IPAC_2026()