from pyg4ometry.fluka.card import Card as _Card

_allowedDefaultsSDUM = ["CALORIME", "EET/TRAN", "EM-CASCA", "ICARUS", "HADROTHE", "NEUTRONS",
                        "NEW-DEFA", "PRECISIO", "SHIELDIN", "DAMAGE"]


class Title:

    def __init__(self, title = ""):
        self.titleCard = _Card("TITLE")
        self.titleTextCard = _Card(title)

    def AddRegistry(self, flukaregistry):
        if self.titleCard :
            flukaregistry.addCard(self.titleCard)
            flukaregistry.addCard(self.titleTextCard)

    def __repr__(self):
        retString = ""
        if self.titleCard :
            retString = self.titleCard.toFreeString()
            retString += '\n'+self.titleTextCard.toFreeString()

        return retString