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

class Defaults:
    def __init__(self, default):
        if default in _allowedDefaultsSDUM :
            self.defaultCard = _Card("DEFAULTS", sdum=default)
        else :
            print("Unallowed default {}, not in {}".format(default, _allowedDefaultsSDUM))
            self.defaultCard = None

    def AddRegistry(self, flukaregistry):
        if self.defaultCard :
            flukaregistry.addCard(self.defaultCard)

    def __repr__(self):
        retString = "DEFAULT : undefined"

        if self.defaultCard :
            retString = self.defaultCard.toFreeString()

        return retString
