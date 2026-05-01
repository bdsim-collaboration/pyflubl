from pyg4ometry.fluka import fluka_registry

import pyflubl as _pfbl
import pyg4ometry as _pyg4
import os as _os

def make_T246_Material() :
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

    s = _pfbl.Fluka.Start(50)
    m.AddStart(s)

    uic = _pfbl.Fluka.Usricall()
    m.AddUsricall(uic)

    ud = _pfbl.Fluka.Userdump(mgdraw=100,lun=23,mgdrawOption=-1,userDump=None, outputFile="dump")
    m.AddUserdump(ud)

    uoc = _pfbl.Fluka.Usrocall()
    m.AddUsrocall(uoc)

    # Make materials (SS 316 )
    fr = m._GetFlukaRegistry(True)
    fm_c  = _pyg4.fluka.Material("C", 6, 2.266, 12, flukaregistry=fr) # graphite density
    fm_mn = _pyg4.fluka.Material("MN", 25, 7.21, 56, flukaregistry=fr) # density range 7.21 - 7.47 g/cm^3
    fm_p  = _pyg4.fluka.Material("P", 15, 1.82, 31, flukaregistry=fr) # white 1.82 g/cm^3
    fm_s  = _pyg4.fluka.Material("S", 16, 2.07, 32,flukaregistry=fr)
    fm_si = _pyg4.fluka.Material("SI", 14, 2.33, 28, flukaregistry=fr)
    fm_cr = _pyg4.fluka.Material("CR", 24, 7.19 , 52, flukaregistry=fr)
    fm_ni = _pyg4.fluka.Material("NI", 28, 8.90, 58, flukaregistry=fr)
    fm_mo = _pyg4.fluka.Material("MO", 42, 10.22, 96, flukaregistry=fr)
    fm_fe = _pyg4.fluka.Material("FE", 26, 7.874, 56, flukaregistry=fr)
    fm_ss = _pyg4.fluka.Compound("SS", 8.0, [(fm_c, 0.08/100),
                                             (fm_mn, 2/100),
                                             (fm_p, 0.045/100),
                                             (fm_s, 0.03/100),
                                             (fm_si, 1/100),
                                             (fm_cr, 16/100),
                                             (fm_ni, 10/100),
                                             (fm_mo, 2/100),
                                             (fm_fe, 68.845/100)],
                                 "mass",
                                 flukaregistry=fr)

    m.AddDrift(name="d1", length=1,
               beampipeMaterial="SS")
    m.AddTarget(name="t1", length=0.1,
                horizontalWidth=200,
                verticalWidth=200,
                apertureType="circular",
                material="FE",
                outerMaterial="AIR")
    m.AddDrift(name="d2", length=0.01,
               beampipeMaterial="SS")
    m.AddSamplerPlane(name="s1", length=1e-6)

    m.SaveJSON(this_dir + "/T246_Material_coordinate.json")
    m.Write(this_dir+"/T246_Material")

    return m

def test_T246_Material() :
    make_T246_Material()

if __name__ == "__main__":
    test_T246_Material()
