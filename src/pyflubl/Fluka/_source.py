from pyg4ometry.fluka.card import Card as _Card
from ._BaseCard import BaseCard as _BaseCard

class Source(_BaseCard):
    def __init__(self,
                 what1 = None,
                 what2 = None,
                 what3 = None,
                 what4 = None,
                 what5 = None,
                 what6 = None,
                 what7 = None,
                 what8 = None,
                 what9 = None,
                 what10 = None,
                 what11 = None,
                 what12 = None,
                 what13 = None,
                 what14 = None,
                 what15 = None,
                 what16 = None,
                 what17 = None,
                 what18 = None,
                 sdum = None):
        super().__init__()

        self.card = _Card("SOURCE",
                          what1, what2, what3,
                          what4, what5, what6,
                          sdum)

        self.cardCont1 = _Card("SOURCE",
                               what7, what8, what9,
                               what10, what11, what12,
                               "&")

        self.cardCont2 = _Card("SOURCE",
                               what13, what14, what15,
                               what16, what17, what18,
                               "&")