from pyg4ometry.fluka.card import Card as _Card
from ._BaseCard import BaseCard as _BaseCard

class Beam1(_BaseCard):

    def __init__(self,
                 momentumOrKe = None,
                 energySpread = None,
                 divergence = None,
                 xWidth = None,
                 yWidth = None,
                 sdum = ""):
        super().__init__()

        self.card = _Card("BEAM",
                          momentumOrKe, energySpread, divergence,
                          xWidth, yWidth, None, sdum)

        # store momentum as will be required to scale magnets
        self._momentum = momentumOrKe

        # store particle as might be needed for mass
        self._particle = sdum

    @property
    def momentum(self):
        return self._momentum

    @momentum.setter
    def momentum(self, value):
        self._momentum = value
        self.card.what1 = value

    @property
    def particle(self):
        return self._particle

    @particle.setter
    def particle(self, value):
        self._particle = value
        self.card.sdum = value

class BeamAxes(_BaseCard):
    def __init__(self,
                 xxCosine = None,
                 xyCosine = None,
                 xzCosine = None,
                 zxCosine = None,
                 zyCosine = None,
                 zzCosine = None,
                 sdum = "") :
        super().__init__()

        self.card = _Card("BEAMAXES",
                          xxCosine, xyCosine, xzCosine,
                          zxCosine, zyCosine, zzCosine,
                          None)

class Beampos(_BaseCard):
    def __init__(self,
                 xCentre = None, yCentre = None ,zCentre = None,
                 xCosine = None, yCosine = None, sdum = None,
                 # sdum = SPHE-VOL
                 innerRadius = None, outerRadius = None,
                 # sdum = CYLI-VOL
                 # innerRadius, outerRadius,
                 innerHeight = None, outerHeight = None,
                 # sdum = CART-VOL
                 innerX = None, outerX = None,
                 innerY = None, outerY = None,
                 innerZ = None, outerZ = None,
                 # sdum = FLOOD
                 radius = None
                 ):
        super().__init__()

        if sdum == "" or sdum == None or sdum == "NEGATIVE":
            self.card = _Card("BEAMPOS",
                              xCentre, yCentre, zCentre,
                              xCosine, yCosine, None,
                              sdum)
        elif sdum == "SPHE-VOL":
            self.card = _Card("BEAMPOS",
                              innerRadius, outerRadius, None,
                              None, None, None,
                              sdum)
        elif sdum == "CYLI-VOL":
            self.card = _Card("BEAMPOS",
                              innerRadius, outerRadius, innerHeight,
                              outerHeight, None, None,
                              sdum)
        elif sdum == "CART-VOL":
            self.card = _Card("BEAMPOS",
                              innerX, outerX, innerY,
                              outerY, innerZ, outerZ,
                              sdum)
        elif sdum == "FLOOD":
            self.card = _Card("BEAMPOS",
                              radius, None, None, None, None, None, sdum)

