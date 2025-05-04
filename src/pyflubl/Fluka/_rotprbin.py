from pyg4ometry.fluka.card import Card as _Card
from ._BaseCard import BaseCard as _BaseCard

class Rotprbin(_BaseCard):
    '''Boundary crossing fluence or current estimator'''

    def __init__(self,
                 storagePrecision=None,
                 rotDefi=None,
                 eventbinPrint=0,
                 usrbinStart=None,
                 usrbinEnd=None,
                 usrbinStep =None,
                 sdum = "",
                 correctionFactors=0) :
        super().__init__()

        if sdum == None :
            self.card = _Card("ROTPRBIN",
                              storagePrecision, rotDefi, eventbinPrint,
                              usrbinStart, usrbinEnd, usrbinStep,
                              None)
        else :
            self.card = _Card("ROTPRBIN",
                              correctionFactors, None, None,
                              usrbinStart, usrbinEnd, usrbinStep,
                              None)