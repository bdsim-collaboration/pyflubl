from pyg4ometry.fluka.card import Card as _Card
from ._BaseCard import BaseCard as _BaseCard

class Elcfield(_BaseCasd):
    def __init__(self):
        def __init__(self,
                     angleMax=None,
                     boundaryError=None,
                     stepLengthMin=None,
                     xE=0,
                     yE=0,
                     zE=0):
            super().__init__()

            self.card = _Card("ELCFIELD",
                              angleMax, boundaryError,stepLengthMin,
                              xE, yE, zE, None)