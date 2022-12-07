from ..FlukaMachine import FlukaMachine as _FlukaMachine

class BaseConverter :

    def __init__(self, samplerThickness = 1e-6, samplerSize = 1000, worldSize = [1000,1000,1000]):
        self.samplerThickness = samplerThickness
        self.samplerSize      = samplerSize
        self.flukaMachine     = _FlukaMachine()

