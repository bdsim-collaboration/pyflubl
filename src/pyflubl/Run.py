from pyg4ometry.fluka.card import Card as _Card

class Randomiz :
    def __init__(self, lun = 1, seed = 54217137):
        self.lun = lun
        self.seed = seed

        self.randomizCard = _Card("RANDOMIZ",lun, seed)

    def AddRegistry(self, flukaregistry):
        if self.randomizCard :
            flukaregistry.addCard(self.randomizCard)

    def __repr__(self):
        retString = ""
        if self.randomizCar :
            retString = self.randomizCard.toFreeString()

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
