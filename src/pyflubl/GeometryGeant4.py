import numpy as _np
import pyg4ometry as _pyg4
from pyg4ometry.transformation import tbxyz2matrix as _tbxyz2matrix

from .Options import Options as _Options

class PlacementType:
    zAligned = 0 # for box like outers
    xAligned = 1 # for trap like outers

    @staticmethod
    def rotationFromPlacementType(placementType) :
        if placementType == PlacementType.xAligned :
            return [0, -_np.pi/2, -_np.pi/2]
        elif placementType == PlacementType.zAligned :
            return [0, 0, 0]
        else :
            raise ValueError("Unknown placement type: {}".format(placementType))

    def translationFromPlacementType(placementType, xdisplacement=0, ydisplacement=0) :
        if placementType == PlacementType.xAligned :
            return [0, xdisplacement, ydisplacement]
        elif placementType == PlacementType.zAligned :
            return [xdisplacement, ydisplacement, 0]


def MakeBeamPipeCircular(g4registry = None,
                         motherLogical = None,
                         name = "circular_beam_pipe",
                         length = 1000,
                         beamPipeRadius = _Options().beampipeRadius,
                         beamPipeThickness = _Options().beampipeThickness,
                         beamPipeMaterialName = _Options().beampipeMaterial,
                         vacuumMaterialName = _Options().vacuumMaterial,
                         e1=0, p1=0,
                         e2=0, p2=0,
                         placement=PlacementType.xAligned) :

    # No registry, so create one
    if g4registry is None:
        g4registry = _pyg4.geant4.Registry()

    # normalise face normals
    faceNormalIn  = _np.array([_np.sin(e1)*_np.cos(p1), _np.sin(e1)*_np.sin(p1), -_np.cos(e1)])
    faceNormalOut = _np.array([_np.sin(e2)*_np.cos(p2), _np.sin(e2)*_np.sin(p2),  _np.cos(e2)])

    # fake materials
    vacuumMaterial = _pyg4.geant4.MaterialSingleElement(name=vacuumMaterialName, atomic_number=1, atomic_weight=1,
                                                        density=1)
    beampipeMaterial = _pyg4.geant4.MaterialSingleElement(name=beamPipeMaterialName, atomic_number=1, atomic_weight=1,
                                                          density=1)

    # make actual beampipe
    bpsolid = _pyg4.geant4.solid.CutTubs(name + "_bp_solid",
                                         0, beamPipeRadius + beamPipeThickness, length,
                                         0, _np.pi * 2,
                                         faceNormalIn,
                                         faceNormalOut,
                                         g4registry)
    bplogical = _pyg4.geant4.LogicalVolume(bpsolid, beampipeMaterial, name + "_bp_lv", g4registry)
    bpphysical = _pyg4.geant4.PhysicalVolume(PlacementType.rotationFromPlacementType(placement), [0, 0, 0], bplogical, name + "_bp_pv",
                                             motherLogical, g4registry)

    vacsolid = _pyg4.geant4.solid.CutTubs(name + "_vac_solid",
                                          0, beamPipeRadius, length,
                                          0, _np.pi * 2,
                                          faceNormalIn,
                                          faceNormalOut,
                                          g4registry)

    vaclogical = _pyg4.geant4.LogicalVolume(vacsolid, vacuumMaterial, name + "_vac_lv", g4registry)
    vacphysical = _pyg4.geant4.PhysicalVolume([0, 0, 0], [0, 0, 0], vaclogical, name + "_vac_pv", bplogical, g4registry)

    return [bplogical, bpphysical, vacphysical]

def MakeBeamPipeElliptical(g4reg):
    pass

def MakeOuterBox(g4registry = None,
                 motherLogical = None,
                 name = "outer_box",
                 length = 1000,
                 outerHorizontalSize = _Options().outerHorizontalSize,
                 outerVerticalSize = _Options().outerVerticalSize,
                 outerMaterial = _Options().outerMaterial):

    # No registry, so create one
    if g4registry is None:
        g4registry = _pyg4.geant4.Registry()

    # fake materials
    outerMaterial = _pyg4.geant4.MaterialSingleElement(name=outerMaterial, atomic_number=1, atomic_weight=1,
                                                       density=1)

    # make actual outer
    outerSolid = _pyg4.geant4.solid.Box(name + "_outer_solid",
                                        length, outerHorizontalSize, outerVerticalSize,
                                        g4registry)
    outerLogical = _pyg4.geant4.LogicalVolume(outerSolid, outerMaterial, name + "_outer_lv", g4registry)

    return [outerLogical, None]


def MakeOuterTrapezoid(g4registry = None,
                       name = "outer_trapezoid",
                       motherLogical = None,
                       tra_coords = _np.array([[-_Options().outerHorizontalSize, -1000],
                                               [-_Options().outerHorizontalSize,  1000],
                                               [ _Options().outerHorizontalSize,  1000],
                                               [ _Options().outerHorizontalSize, -1000],
                                               [-_Options().outerHorizontalSize, -1000],
                                               [-_Options().outerHorizontalSize,  1000],
                                               [ _Options().outerHorizontalSize,  1000],
                                               [ _Options().outerHorizontalSize, -1000]]),
                       outerVerticalSize = _Options().outerVerticalSize,
                       outerMaterial = _Options().outerMaterial) :

    # No registry, so create one
    if g4registry is None:
        g4registry = _pyg4.geant4.Registry()

    # fake materials
    outerMaterial = _pyg4.geant4.MaterialSingleElement(name=outerMaterial, atomic_number=1, atomic_weight=1,
                                                       density=1)

    # make actual trapezoid outer
    outerSolid = _pyg4.geant4.solid.GenericTrap(name + "_solid",
                                               tra_coords[0][0], tra_coords[0][1],
                                               tra_coords[1][0], tra_coords[1][1],
                                               tra_coords[2][0], tra_coords[2][1],
                                               tra_coords[3][0], tra_coords[3][1],
                                               tra_coords[4][0], tra_coords[4][1],
                                               tra_coords[5][0], tra_coords[5][1],
                                               tra_coords[6][0], tra_coords[6][1],
                                               tra_coords[7][0], tra_coords[7][1],
                                               outerVerticalSize/2, g4registry)

    outerLogical = _pyg4.geant4.LogicalVolume(outerSolid, outerMaterial, name + "_outer_lv", g4registry)

    outerPhysical = _pyg4.geant4.PhysicalVolume([0,-_np.pi/2,-_np.pi/2],[0,0,0],outerLogical,name+"_outer_pv",
                                                motherLogical,g4registry)

    return [outerLogical, outerPhysical]

def MakeTarget(g4registry = None,
               name = "target",
               motherLogical = None,
               apertureType = "rectangular",
               length=1000,
               material="IRON",
               horizontalWidth = _Options().outerHorizontalSize,
               verticalWidth = _Options().outerVerticalSize,
               placement = PlacementType.xAligned):

    if apertureType == "rectangular":
        targetsolid = _pyg4.geant4.solid.Box(name + "_target_solid", horizontalWidth, verticalWidth, length, g4registry)
    elif apertureType == "circular" or apertureType == "elliptical":
        targetsolid = _pyg4.geant4.solid.EllipticalTube(name + "_target_solid", horizontalWidth, verticalWidth, length,
                                                        g4registry)
    else:
        targetsolid = _pyg4.geant4.solid.Box(name + "_target_solid", horizontalWidth, verticalWidth, length, g4registry)

    # fake materials
    materialFake = _pyg4.geant4.MaterialSingleElement(name=material, atomic_number=1, atomic_weight=1,density=1)

    targetlogical = _pyg4.geant4.LogicalVolume(targetsolid, materialFake, name + "_targe_lv", g4registry)
    targetphysical = _pyg4.geant4.PhysicalVolume(PlacementType.rotationFromPlacementType(placement),
                                                 [0, 0, 0],
                                                 targetlogical,
                                                 name + "_taget_pv",
                                                 motherLogical,
                                                 g4registry)

    return [targetlogical, targetphysical]

def MakeRCol(g4registry = None,
             name="rcol",
             motherLogical=None,
             length=1000,
             material="IRON",
             horizontalWidth=_Options().outerHorizontalSize,
             verticalWidth=_Options().outerVerticalSize,
             xsize=0,
             ysize=0,
             placement=PlacementType.xAligned):


    collimatorsolid1 = _pyg4.geant4.solid.Box(name + "_rcol1_solid", horizontalWidth, verticalWidth, length, g4registry)
    collimatorsolid2 = _pyg4.geant4.solid.Box(name + "_rcol2_solid", xsize, ysize, length, g4registry)

    if xsize == 0 or ysize == 0:
        collimatorsolid = collimatorsolid1
    else:
        collimatorsolid = _pyg4.geant4.solid.Subtraction(name + "_rcol_solid", collimatorsolid1, collimatorsolid2,
                                                         [[0, 0, 0], [0, 0, 0]], g4registry)

    collimatorLogical = _pyg4.geant4.LogicalVolume(collimatorsolid, material, name + "_rcol_lv", g4registry)
    collimatorPhysical = _pyg4.geant4.PhysicalVolume(PlacementType.rotationFromPlacementType(placement),
                                                     [0, 0, 0],
                                                     collimatorLogical,
                                                     name + "_rcol_pv",
                                                     motherLogical,
                                                     g4registry)

    return [collimatorLogical, collimatorPhysical]

def MakeECol(g4registry = None,
             name="ecol",
             motherLogical=None,
             length=1000,
             material="IRON",
             horizontalWidth=_Options().outerHorizontalSize,
             verticalWidth=_Options().outerVerticalSize,
             xsize=0,
             ysize=0,
             placement=PlacementType.xAligned):

    collimatorsolid1 = _pyg4.geant4.solid.Box(name + "_rcol1_solid", horizontalWidth, verticalWidth, length, g4registry)
    collimatorsolid2 = _pyg4.geant4.solid.EllipticalTube(name + "_rcol2_solid", xsize, ysize, length, g4registry)

    if xsize == 0 or ysize == 0:
        collimatorSolid = collimatorsolid1
    else:
        collimatorSolid = _pyg4.geant4.solid.Subtraction(name + "_rcol_solid",
                                                         collimatorsolid1,
                                                         collimatorsolid2,
                                                         [[0, 0, 0], [0, 0, 0]],
                                                         g4registry)

    collimatorLogical = _pyg4.geant4.LogicalVolume(collimatorSolid, material, name + "_rcol_lv", g4registry)
    collimatorPhysical = _pyg4.geant4.PhysicalVolume(PlacementType.rotationFromPlacementType(placement),
                                                     [0, 0, 0],
                                                     collimatorLogical,
                                                     name + "_rcol_pv",
                                                     motherLogical,
                                                     g4registry)

    return [collimatorLogical, collimatorPhysical]

def MakeJCol(g4registry = None,
             name="jcol",
             motherLogical=None,
             length=1000,
             material="IRON",
             horizontalWidth=0,
             verticalWidth=0,
             xsize=0,
             ysize=0,
             xsizeLeft=0,
             xsizeRight=0,
             jawTiltLeft=0,
             jawTiltRight=0,
             placement=PlacementType.xAligned) :

    # default left size
    leftwidth = horizontalWidth / 2 - xsize / 2
    # default right size
    rightwidth = leftwidth

    leftcentre = xsize + leftwidth / 2
    rightcentre = -xsize - rightwidth / 2

    if xsizeLeft != 0:
        leftwidth = horizontalWidth / 2
        leftcentre = xsizeLeft + leftwidth / 2

    if xsizeRight != 0:
        rightwidth = horizontalWidth / 2
        rightcentre = - xsizeRight - rightwidth / 2

    if jawTiltLeft == 0 and jawTiltRight == 0:

        leftsolid = _pyg4.geant4.solid.Box(name + "_jcol_left_solid", leftwidth, verticalWidth, length,
                                           g4registry)
        rightsolid = _pyg4.geant4.solid.Box(name + "_jcol_right_solid", rightwidth, verticalWidth, length,
                                            g4registry)

        rightlogical = _pyg4.geant4.LogicalVolume(rightsolid, material, name + "_rcol_right_lv", g4registry)
        rightphysical = _pyg4.geant4.PhysicalVolume(PlacementType.rotationFromPlacementType(placement),
                                                    PlacementType.translationFromPlacementType(placement, rightcentre,0),
                                                    rightlogical,
                                                    name + "_jcol_right_pv",
                                                    motherLogical,
                                                    g4registry)

        leftlogical = _pyg4.geant4.LogicalVolume(leftsolid, material, name + "_rcol_left_lv", g4registry)
        leftphysical = _pyg4.geant4.PhysicalVolume(PlacementType.rotationFromPlacementType(placement),
                                                   PlacementType.translationFromPlacementType(placement,leftcentre, 0),
                                                   leftlogical,
                                                   name + "_jcol_left_pv",
                                                   motherLogical,
                                                   g4registry)

        return [leftlogical, leftphysical], [rightlogical, rightphysical]
    else:
        # TODO complete tilted RCol and zero gap
        pass


def MakeShield(g4registry = None,
               name="shield",
               motherLogical=None,
               length=1000,
               material="IRON",
               horizontalWidth=_Options().outerHorizontalSize,
               verticalWidth=_Options().outerVerticalSize,
               xsize=0,
               ysize=0,
               placement=PlacementType.xAligned) :

    # make shield and add to outer logical
    shieldsolid1 = _pyg4.geant4.solid.Box(name + "_shield1_solid", horizontalWidth, verticalWidth, length , g4registry)
    shieldsolid2 = _pyg4.geant4.solid.Box(name + "_shield2_solid", xsize, ysize, length, g4registry)
    shieldsolid = _pyg4.geant4.solid.Subtraction(name + "_shield_sold", shieldsolid1, shieldsolid2,
                                                 [[0, 0, 0], [0, 0, 0]], g4registry)
    shieldLogical = _pyg4.geant4.LogicalVolume(shieldsolid, material, name + "_shield_lv", g4registry)
    shieldPhysical = _pyg4.geant4.PhysicalVolume(PlacementType.rotationFromPlacementType(placement),
                                                 [0, 0, 0],
                                                 shieldLogical,
                                                 name + "_shield_pv",
                                                 motherLogical,
                                                 g4registry)

    return [shieldLogical, shieldPhysical]

def MakeDump(g4registry = None,
             name="dump",
             motherLogical=None,
             length=1000,
             material="BLCKHOLE",
             horizontalWidth=_Options().outerHorizontalSize,
             verticalWidth=_Options().outerVerticalSize,
             apertureType="rectangular",
             placement=PlacementType.xAligned) :

    dumpMaterial = _pyg4.geant4.MaterialSingleElement(material, atomic_number=1, atomic_weight=1, density=1)

    if apertureType == "rectangle":
        targetsolid = _pyg4.geant4.solid.Box(name + "_target_solid", horizontalWidth, verticalWidth, length, g4registry)
    elif apertureType == "circular" or apertureType == "elliptical":
        targetsolid = _pyg4.geant4.solid.EllipticalTube(name + "_target_solid", horizontalWidth, verticalWidth, length,
                                                        g4registry)
    else:
        targetsolid = _pyg4.geant4.solid.Box(name + "_target_solid", horizontalWidth, verticalWidth, length, g4registry)

    targetLogical = _pyg4.geant4.LogicalVolume(targetsolid, dumpMaterial, name + "_targe_lv", g4registry)
    targetPhysical = _pyg4.geant4.PhysicalVolume(PlacementType.rotationFromPlacementType(placement),
                                                 [0, 0, 0],
                                                 targetLogical,
                                                 name + "_taget_pv",
                                                 motherLogical,
                                                 g4registry)
    return [targetLogical, targetPhysical]

def MakeWireScanner(g4registry = None,
                    name="wirescanner",
                    motherLogical=None,
                    wireMaterial="IRON",
                    wireDiameter=10,
                    wireLength=50,
                    wireAngle=0.0,
                    wireOffsetX=0.0,
                    wireOffsetY=0.0,
                    wireOffsetZ=0.0,
                    placement=PlacementType.xAligned):

    print("g4registry",g4registry)
    print("name",name)
    print("motherLogical",motherLogical)
    print("wireMaterial",wireMaterial)
    print("wireDiameter",wireDiameter)
    print("wireLength",wireLength)
    print("wireAngle",wireAngle)
    print("wireOffsetX",wireOffsetX)
    print("wireOffsetY",wireOffsetY)
    print("wireOffsetZ",wireOffsetZ)


    wireSolid = _pyg4.geant4.solid.Tubs(name + "_wire_solid", 0, wireDiameter / 2, wireLength, 0, 2 * _np.pi,
                                        g4registry)

    wireLogical = _pyg4.geant4.LogicalVolume(wireSolid, wireMaterial, name + "__wire_lv", g4registry)
    wirePhysical = _pyg4.geant4.PhysicalVolume([_np.pi / 2, wireAngle, 0],
                                               [wireOffsetX, wireOffsetY, wireOffsetZ],
                                               wireLogical,
                                               name + "_wire_pv",
                                               motherLogical,
                                               g4registry)
    return [wireLogical, wirePhysical]

def DrawGeometry(logical) :
    v = _pyg4.visualisation.VtkViewerNew()
    v.addLogicalVolume(logical)
    v.buildPipelinesAppend()
    v.addAxes(500)
    v.view()

def SaveGeometry(g4registry, filename) :
    w = _pyg4.gdml.Writer()
    w.addDetector(g4registry)
    w.write(filename)