import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.visualisation as _vi
import os as _os

def test_T032_Custom_Pyg4(vis=False, interactive=False) :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "5000", reg, True)
    wy = _gd.Constant("wy", "5000", reg, True)
    wz = _gd.Constant("wz", "5000", reg, True)

    bx = _gd.Constant("bx", "1000", reg, True)
    by = _gd.Constant("by", "1000", reg, True)
    bz = _gd.Constant("bz", "1000", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Au")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    bs1 = _g4.solid.Box("bs1", 50, 50, 50, reg, "mm")


    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)

    bl1 = _g4.LogicalVolume(bs1, bm, "bl1", reg)

    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)
    bp1 = _g4.PhysicalVolume([0,0,0], [-400,0,-400], bl1, "b2_pv1", bl, reg)

    # set world volume
    reg.setWorld(wl.name)

    if vis:
        v = _vi.VtkViewerNew()
        v.addLogicalVolume(reg.getWorldVolume())
        v.buildPipelinesAppend()
        v.view(interactive=interactive)

    w = _gd.Writer()
    w.addDetector(reg)
    w.write(this_dir+"/test_T032_Custom_Pyg4.gdml")

