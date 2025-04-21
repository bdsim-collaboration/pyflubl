from pyg4ometry.fluka.card import Card as _Card

_allowedDefaultsSDUM = ["CALORIME", "EET/TRAN", "EM-CASCA", "ICARUS", "HADROTHE", "NEUTRONS",
                        "NEW-DEFA", "PRECISIO", "SHIELDIN", "DAMAGE"]

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
