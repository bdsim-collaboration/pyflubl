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