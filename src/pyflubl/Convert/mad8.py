from .baseConverter import BaseConverter as _BaseConverter

class Mad8(_BaseConverter) :

    def __init__(self, mad8TFSFileName, addSamplers = True, samplerThickness = 1e-6, samplerSize = 1000):
        # base class init
        super().__init__(samplerThickness,samplerSize)

        # derived class init
        self.mad8TFSFileName = mad8TFSFileName

    def toFluka(self):
        pass


