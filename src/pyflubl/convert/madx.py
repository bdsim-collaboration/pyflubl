from .baseConverter import BaseConverter as _BaseConverter

class Madx(_BaseConverter) :

    def __init__(self, madxTFSFileName, addSamplers = True, samplerThickness = 1e-6, samplerSize = 1000):
        # base class init
        super().__init__(samplerThickness,samplerSize)

        # derived class init
        self.madxTFSFileName = madxTFSFileName

    def toFluka(self):
        pass
