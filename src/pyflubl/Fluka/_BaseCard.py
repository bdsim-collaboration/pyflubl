from pyg4ometry.fluka.card import Card as _Card

class BaseCard:

    def __init__(self):
        self.card = _Card("",
                          None, None, None,
                          None, None, None,
                          "")
        self.cardCont1 = None
        self.cardCont2 = None

    def AddRegistry(self, flukaregistry):
        if self.card :
            flukaregistry.addCard(self.card)
        if self.cardCont1 :
            flukaregistry.addCard(self.cardCont1)
        if self.cardCont2 :
            flukaregistry.addCard(self.cardCont2)

    def __repr__(self):
        retString = ""
        if self.card :
            retString = self.card.toFreeString()
        if self.cardCont1 :
            retString += "\n"
            retString += self.cardCont1.toFreeString()
        if self.cardCont2 :
            retString += "\n"
            retString += self.cardCont2.toFreeString()

        return retString