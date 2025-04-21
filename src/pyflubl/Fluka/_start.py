from pyg4ometry.fluka.card import Card as _Card

class Start :

    def __init__(self, nHistories = 5000, termTime = 80, coreDump = 1, randCalls = 1, inactiveTime = None):
        self.nHistories = nHistories
        self.termTime = termTime
        self.coreDump = coreDump
        self.randCalls = randCalls
        self.inactiveTime = inactiveTime

        self.startCard = _Card("START",
                               self.nHistories,None,self.termTime,
                               self.coreDump,self.randCalls,self.inactiveTime)

    def AddRegistry(self, flukaregistry):
        if self.startCard :
            flukaregistry.addCard(self.startCard)

    def __repr__(self):
        retString = ""
        if self.startCard :
            retString = self.startCard.toFreeString()
        return retString