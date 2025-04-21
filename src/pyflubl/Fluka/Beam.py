from pyg4ometry.fluka.card import Card as _Card
class Beam :
    def __init__(self,
                 energy=1.0, # BEAM WHAT(1) >0.0 GeV/c <0.0 GeV
                 energySpread=0.0, # BEAM WHAT(2) >0.0 GeV, <0.0 FWHM of gaussian
                 beamDivergence=0.0, # BEAM WHAT(3) >0 rectangular width, > 2000*PI isotropic, < 0.0 FWHM gaussian
                 beamWidthX=0.0, # BEAM WHAT(4) >= 0 rectangular beam width in x in cm, <0 gaussian x beam FWHM
                 beamWidthY=0.0, # BEAM WHAT(5) >= 0 rectangular beam width in y in cm, <0 gaussian y beam FWHM
                 annular=0, # BEAM WHAT(6) < 0 ignore beamWidthX/Y
                 beamRadiusMaximum=0.0, # BEAM WHAT(4)
                 beamRadiusMinimum=0.0, # BEAM WHAT(5)
                 particleType='ELECTRON', # SDUM
                 ):
        self.energy = energy
        self.energySpread = energySpread
        self.beamDivergence = beamDivergence
        self.beamWidthX = beamWidthX
        self.beamWidthY = beamWidthY
        self.annular = annular
        self.beamRadiusMaximum = beamRadiusMaximum
        self.beamRadiusMinimum = beamRadiusMinimum
        self.particleType = particleType

        if annular >= 0 :
            self.beamCard = _Card("BEAM",self.energy, self.energySpread, self.beamDivergence,
                                  self.beamWidthX, self.beamWidthY, self.annular, self.particleType)
        else :
            self.beamCard = _Card("BEAM",self.energy, self.energySpread, self.beamDivergence,
                                  self.beamRadiusMaximum, self.beamRadiusMinimum, self.annular, self.particleType)

        self.beamposCard = None
        self.beamposExtraCard = None
        self.beamaxesCard = None
        self.beamposFloodCard = None

    def AddBeamPosition(self,
                        x, # WHAT(1)
                        y, # WHAT(2)
                        z, # WHAT(3)
                        xDirCosine, # WHAT(4)
                        yDirCosine, # WHAR(5)
                        negativeZ = "" # DSUM
                        ):

        self.x = x
        self.y = y
        self.z = z
        self.xDirCosine = xDirCosine
        self.yDirCosine = yDirCosine
        self.negativeZ = negativeZ
        self.beamposCard = _Card("BEAMPOS", self.x, self.y, self.z,
                                 self.xDirCosine, self.yDirCosine, None, self.negativeZ)

    def AddBeamPositionDSUMSPHEVOL(self,
                                    sphereInnerRadius=0.0,
                                    sphereOuterRadius=0.0):
        dsum = "SPHE-VOL"

        self.sphereInnerRadius = sphereInnerRadius
        self.sphereOuterRadius = sphereOuterRadius

        self.beamposExtraCard = _Card("BEAMPOS", self.sphereInnerRadius, self.sphereOuterRadius, None,
                                      None, None, None, dsum)
    def AddBeamPositionDSUMCYLIVOL(self,
                                   cylinderInnerRadius=0.0,
                                   cylinderOuterRadius=0.0,
                                   cylinderInnerHeight=0.0,
                                   cylinderOuterHeight=0.0):
        dsum = "CYLI-VOL"

        self.cylinderInnerRadius = cylinderInnerRadius
        self.cylinderOuterRadius = cylinderOuterRadius
        self.cylinderInnerHeight = cylinderInnerHeight
        self.cylinderOuterHeight = cylinderOuterHeight

        self.beamposExtraCard = _Card("BEAMPOS",
                                      self.cylinderInnerRadius, self.cylinderOuterRadius,
                                      self.cylinderInnerHeight, cylinderOuterHeight,
                                      None, None, dsum)


    def AddBeamPositionDSUMCARTVOL(self,
                                   cartInnerX=0.0,
                                   cartOuterX=0.0,
                                   cartInnerY=0.0,
                                   cartOuterY=0.0,
                                   cartInnerZ=0.0,
                                   cartOuterZ=0.0):
        dsum = "CART-VOL"

        self.cartInnerX = cartInnerX
        self.cartOuterX = cartOuterX
        self.cartInnerY = cartInnerY
        self.cartOuterY = cartOuterY
        self.cartInnerZ = cartInnerZ
        self.cartOuterZ = cartOuterZ

        self.beamposExtraCard = _Card("BEAMPOS",
                                      self.cartInnerX, self.cartOuterX,
                                      self.cartInnerY, self.cartOuterY,
                                      self.cartInnerZ, self.cartOuterZ,
                                      dsum)

    def AddBeamPositionDSUMFLOOD(self, #
                                 radius,  # WHAT(1) for BEAMPOS w1 w2 w3 w4 w5 w6 FLOOD
                                 ):
        dsum = "FLOOD"

        self.radius = radius

        self.beamposExtraCard = _Card("BEAMPOS", self.radius, None, None, None, None, None, dsum)

    def AddBeamAxes(self,
                    xxCosine = 1,
                    xyCosine = 0,
                    xzCosine = 0,
                    zxCosine = 0,
                    zyCosine = 0,
                    zzCosine = 1):

        self.xxCosine = xxCosine
        self.xyCosine = xyCosine
        self.xzCosine = xzCosine
        self.zxCosine = zxCosine
        self.zyCosine = zyCosine
        self.zzCosine = zzCosine

        self.beamaxesCard = _Card("BEAMAXES",
                                  self.xxCosine, self.xyCosine, self.xzCosine,
                                  self.zxCosine, self.zyCosine, self.zzCosine, "")

    def AddRegistry(self, flukaregistry):
        flukaregistry.addCard(self.beamCard)
        if self.beamposCard :
            flukaregistry.addCard(self.beamposCard)
        if self.beamposExtraCard :
            flukaregistry.addCard(self.beamposExtraCard)
        if self.beamaxesCard :
            flukaregistry.addCard(self.beamaxesCard)

    def __repr__(self):
        retString = self.beamCard.toFreeString()

        if self.beamposCard :
            retString += "\n"+self.beamposCard.toFreeString()
        if self.beamposExtraCard :
            retString += "\n"+self.beamposExtraCard.toFreeString()
        if self.beamaxesCard :
            retString += "\n"+self.beamaxesCard.toFreeString()

        return retString