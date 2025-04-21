from pyg4ometry.fluka.card import Card as _Card

class Global:
    def __init__(self, maxRegions = None, howAnalogue = None, dNear = None,
                 input = None, inputGeometry = None, memory = None):
        self.globalCard = _Card("GLOBAL", maxRegions, howAnalogue, dNear, input, inputGeometry, memory)

    def AddRegistry(self, flukaregistry):
        if self.globalCard :
            flukaregistry.addCard(self.globalCard)

    def __repr__(self):
        if self.globalCard :
            retString = self.globalCard.toFreeString()

        return retString