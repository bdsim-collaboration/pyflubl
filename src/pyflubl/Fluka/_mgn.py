from pyg4ometry.fluka.card import Card as _Card
from ._BaseCard import BaseCard as _BaseCard

class Mgnfield(_BaseCard):

    def __init__(self,
                 maxAngle = 30,
                 boundaryIntersectionError = 0.05,
                 minStepLength = 0.1,
                 bx = 0,
                 by = 0,
                 bz = 0,
                 sdum = "",
                 strength = 0,
                 rotDefini = "IDENT",
                 applyRegion = 0,
                 regionFrom = 0,
                 regionTo = None,
                 regionStep = None):

        super().__init__()

        if sdum == "":
            self.card = _Card("MGNFIELD", maxAngle, boundaryIntersectionError,
                              minStepLength, bx, by, bz, sdum)
        else:
            self.card = _Card("MGNFIELD",strength, rotDefini, applyRegion,
                              regionFrom, regionTo, regionStep, sdum)

class Mgncreat(_BaseCard):

    INTERPOLATED = 0
    CONSTANT = 1
    DIPOLE = 2
    QUADRUPOLE = 4
    SEXTUPOLE = 6
    OCTUPOLE = 8
    DECAPOLE = 10

    def __init__(self,
                 fieldType : int = 0,
                 applicableRadius : float = 0.0,
                 xOffset : float = 0.0,
                 yOffset : float = 0.0,
                 mirrorSymmetry : int = 0,
                 sdum : str = "",
                 const_x_fld : float  = 0,
                 const_y_fld : float = 0,
                 const_z_fld : float = 0,
                 nxr_pts : int= 0,
                 ny_pts : int = 0,
                 nz_pts : int = 0,
                 xr_min : float = 0,
                 y_min : float = 0,
                 z_min : float = 0,
                 xr_max : float = 0,
                 y_max : float = 0,
                 z_max : float = 0):

        super().__init__()

        self.card = _Card("MGNCREAT",
                          fieldType, applicableRadius, xOffset, yOffset,
                          mirrorSymmetry, None, sdum)
        self.cardCont1 = None
        self.cardCont2 = None

        if const_x_fld != 0 or \
           const_y_fld != 0 or \
           const_z_fld != 0 or \
           nxr_pts != 0 or \
           ny_pts != 0 or \
           nz_pts != 0 :
            self.cardCont1 = _Card("        ",
                                   const_x_fld, const_y_fld, const_z_fld,
                                   nxr_pts, ny_pts, nz_pts)
        if xr_min != 0 or \
           y_min != 0 or \
           z_min != 0 or \
           xr_max != 0 or \
           y_max != 0 or \
           z_max !=0 :
            self.cardCont2 = _Card("        ",
                                   xr_min, y_min, z_min,
                                   xr_max, y_max, z_max)



class Mgndata(_BaseCard):

    def __init__(self, bxr=0, by=0, bz=0, sdum=""):
        super().__init__()

        self.card = _Card("MGNDATA",bxr,by,bz,
                          None, None, None, sdum)