from pyg4ometry.fluka.card import Card as _Card

class BaseCard:

    def __init__(self):
        self.card = _Card("",
                          None, None, None,
                          None, None, None,
                          "")
        self.cardCont1 = None
        self.cardCont2 = None
        self.cardCont3 = None

    def AddRegistry(self, flukaregistry):
        if self.card :
            flukaregistry.addCard(self.card)
        if self.cardCont1 :
            flukaregistry.addCard(self.cardCont1)
        if self.cardCont2 :
            flukaregistry.addCard(self.cardCont2)
        if self.cardCont3 :
            flukaregistry.addCard(self.cardCont3)

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
        if self.cardCont3 :
            retString += "\n"
            retString += self.cardCont3.toFreeString()

        return retString

    def toFreeString(self):
        return self.__repr__()
