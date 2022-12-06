
import pyg4ometry.fluka as _flu

class FlukaMachine :

    def __init__(self, useLattice = False):
        self.flukaRegistry = _flu.FlukaRegistry()
        self.useLattice = useLattice

    def placeElement(self, pos=[0,0,0], rot=[0,0,0], element = None):
        if type(element) == str :
            # search in databases (geant4)
            pass

        if type(element) == list :
            # saerch in databases (fluka)
            pass

    def exportINP(self):
        pass

    def exportFLAIR(self):
        pass