import numpy as _np
import pyg4ometry as _pyg4
def Build(name,
          outer_x, outer_y, outer_z, outer_material,
          bp_outer_radius, bp_inner_radius, bp_material,
          vac_material) :

    length_safety = 1
    reg = _pyg4.geant4.Registry()

    # make box of correct size
    bpoutersolid = _pyg4.geant4.solid.Box(name+"_outer_solid", outer_x, outer_y, outer_z, reg)
    bpouterlogical = _pyg4.geant4.LogicalVolume(bpoutersolid, outer_material, name + "_outer_lv", reg)
    bpouterphysical = _pyg4.geant4.PhysicalVolume([0, 0, 0], [0, 0, 0], bpouterlogical, name + "_outer_pv", None, reg)

    # make beampipe
    bpsolid = _pyg4.geant4.solid.CutTubs(name+"_bp_solid", bp_inner_radius, bp_outer_radius, outer_z, 0, _np.pi * 2,[0, 0, -1], [0, 0, 1], reg)
    bplogical = _pyg4.geant4.LogicalVolume(bpsolid, bp_material, name + "_bp_lv", reg)
    bpphysical = _pyg4.geant4.PhysicalVolume([0, 0, 0], [0, 0, 0], bplogical, name + "_bp_pv", bpouterlogical, reg)

    # make vaccum solid
    vacsolid = _pyg4.geant4.solid.Tubs(name+"_vac_solid", 0, bp_inner_radius-length_safety, outer_z, 0, _np.pi *2, reg)
    vaclogical = _pyg4.geant4.LogicalVolume(vacsolid, "G4_Galactic", name + "_vac_lv", reg)
    vacphysical = _pyg4.geant4.PhysicalVolume([0, 0, 0], [0, 0, 0], vaclogical, name + "_vac_pv", bplogical, reg)

    reg.setWorldVolume(bpouterlogical)

    return reg
