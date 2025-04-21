
import numpy as _np
class ScorerBoundary :

    def __init__(self, region1Name, region2Name,
                 binning =1.0, oneOrTwoWay = 0.0, currentOrFluence = 0.0,
                 particle = 'ALL-PART', lun = 21, area = -1):

        self.binning = binning
        self.oneOrTwoAway = oneOrTwoWay
        self.currentOrFluence = currentOrFluence
        self.what1 = self.binning + self.oneOrTwoAway * 10 + self.currentOrFluence * 100 # WHAT(1)
        self.particle = particle # WHAT(2)
        self.lun = lun # WHAT(3)
        self.region1Name = region1Name # WHAT(4)
        self.region2Name = region2Name # WHAT(5)
        self.area = area # WHAT(6) area of detector in cm^2. -1 means it is calculated from the geometry

    def SetBinning(self,
                   maxKE=-1, minKE = 0, nKE = 10,
                   maxSolidAngle = 2*_np.pi, minSolidAngle = 0.0, nSolidAngle = 3):
        self.maxKE = maxKE # continuation WHAT(1)
        self.minKE = minKE # continuation WHAT(2)
        self.nKE = nKE # continuation WHAT(3)
        self.maxSolidAngle = maxSolidAngle # continuation WHAT(4)
        self.minSolidAngle = minSolidAngle # continuation WHAT(5)
        self.minSolidAngle = nSolidAngle # continuation WHAT(6)






