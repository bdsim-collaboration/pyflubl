from pyg4ometry.fluka.card import Card as _Card
class Userdump :
    def __init__(self, mgdraw, lun, mgdrawOption, userDump, outputFile):
        self.mgdraw = mgdraw # WHAT(1)
        self.lun = lun # WHAT(2)
        self.mgdrawOption = mgdrawOption # WHAT(3)
        self.userDump = userDump # WHAT(4)
        self.fileName = outputFile # SDUM

        self.userdumpCard = _Card("USERDUMP",
                                  self.mgdraw, self.lun, self.mgdrawOption,
                                  self.userDump, None,None,self.fileName)

    def AddRegistry(self, flukaregistry):
        if self.userdumpCard :
            flukaregistry.addCard(self.userdumpCard)

    def __repr__(self):
        retString = ""
        if self.userdumpCard :
            retString = self.userdumpCard.toFreeString()
        return retString

