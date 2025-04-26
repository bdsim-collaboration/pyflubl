from pyg4ometry.fluka.card import Card as _Card
from ._BaseCard import BaseCard as _BaseCard

class Usrtrack(_BaseCard):
        '''track-length fluence estimator'''

        def __init__(self,
                     logLin = 1, particleType = 201.0, lun = -22,
                     region = 1, volume =1, nbin = 10, sdum ="track1",
                     maxKE = None, minKE = 0) :
            super().__init__()
            self.card = _Card("USRTRACK",
                              logLin, particleType, lun, region,
                              volume, nbin, sdum)
            self.cardCont1 = _Card("USRTRACK",maxKE, minKE, None, None, None, None, "&")
