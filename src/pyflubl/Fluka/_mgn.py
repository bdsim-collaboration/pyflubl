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
                 fieldType = 0,
                 applicableRadius = 0,
                 xOffset = 0,
                 yOffset = 0,
                 mirrorSymmetry = 0,
                 sdum = ""):

        super().__init__()

        self.card = _Card("MGNCREAT",
                          fieldType, applicableRadius, xOffset, yOffset,
                          mirrorSymmetry, None, sdum)
        self.cardCont1 = None

class Mgndata(_BaseCard):

    def __init__(self, bxr=0, by=0, bz=0, sdum=""):
        super().__init__()

        self.card = _Card("MGNDATA",bxr,by,bz,
                          None, None, None, sdum)