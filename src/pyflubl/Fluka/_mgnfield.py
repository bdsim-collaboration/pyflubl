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
                 applyRegion = 0):

        super().__init__()

        if dsum == "":
            self.card = _Card("MGNFIELD", maxAngle, boundaryIntersectionError,
                              minStepLength, bx, by, bz, sdum)
        else:
            self.card = _Card("MGNFIELD",strength, rotDefini,applyRegion,
                              None,None,None,sdum)



