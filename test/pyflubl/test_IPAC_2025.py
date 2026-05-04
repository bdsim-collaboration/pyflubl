import pyflubl as _pfbl
import pyg4ometry as _pyg4
import numpy as _np
import os as _os

from pydantic.v1.json import custom_pydantic_encoder


def IPAC_2025() :

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
    
    m.AddDrift(name="d1", length=1, beampipeMaterial = "TUNGSTEN")
    #m.AddSBend(name="b1", length=1, angle=_np.pi / 8)
    m.AddSBendSplit(name="b1", length=1, angle=_np.pi/8)
    m.AddDrift(name="d2", length=1, beampipeMaterial = "TUNGSTEN")
    #m.AddSBend(name="b2", length=1, angle=-_np.pi / 8)
    m.AddSBendSplit(name="b2", length=1, angle=-_np.pi/8)
    m.AddSamplerPlane(name="s1", length=10e-6)
    m.AddCustomFlukaFile(name="c1", length=1.000,
                         geometryFile=this_dir+"/geometryInput/test_T035_Custom_Fluka_Gap.inp",
                         customOuterRegion='OUTER',
                         customOuterBodies= ['outer'],
                         customRegions=['OUTER','SHIELD','BEAM','TARGET'])

    m.AddSamplerPlane(name="s2", length=10e-6)
    m.AddDrift(name="d3", length=0.5, beampipeMaterial = "TUNGSTEN")
    
    eb1 = _pfbl.Fluka.Usrbin(binning=_pfbl.Fluka.Usrbin.CARTESIAN_STEP,
                             particle="ALL-PART",lun=-24,
                             xmax=150, ymax=150, zmax=150, sdum="eb1",
                             xmin=-150, ymin=-150, zmin=-150,
                             nxbin=201, nybin=201, nzbin=201)
    m.AddUsrbinToElement("c1", eb1)


    m.Write("IPAC_2025", prettyJSON=False)

    return m

def test_IPAC_2025() :
    IPAC_2025()

if __name__ == "__main__":
    test_IPAC_2025()
