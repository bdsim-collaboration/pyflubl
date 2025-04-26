from pyg4ometry.fluka.card import Card as _Card
from ._BaseCard import BaseCard as _BaseCard

class Usrbdx(_BaseCard):
    '''Boundary crossing fluence or current estimator'''

    def __init__(self,
                 binning =1 , partType = "ALL-PART", lun = -22,
                 region1 = 1, region2 = 2, area = 1, sdum = "bdx1",
                 maxKE = None, minKE= 0, nEbin = 10, maxSA = 10,
                 linLogSA = 0.0, nSAbin =1  ) :

        super().__init__()

        self.card = _Card("USRBDX",
                          binning, partType, lun, region1,
                          region2, area, sdum)

        self.cardCont1 = _Card("USRBDX",
                               maxKE, minKE, nEbin, maxSA,
                               linLogSA, nSAbin, "&")
