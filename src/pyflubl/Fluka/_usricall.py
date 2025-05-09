from pyg4ometry.fluka.card import Card as _Card
from ._BaseCard import BaseCard as _BaseCard

class Usricall(_BaseCard):
    def __init__(self,
                 what1 = None,
                 what2 = None,
                 what3 = None,
                 what4 = None,
                 what5 = None,
                 what6 = None,
                 sdum = None):
        super().__init__()

        self.card = _Card("USRICALL",
                          what1, what2, what3,
                          what4, what5, what6,
                          sdum)