from pyg4ometry.fluka.card import Card as _Card
from ._BaseCard import BaseCard as _BaseCard

class Mgncreat(_BaseCard):

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
