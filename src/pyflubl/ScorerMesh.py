
class ScorerMesh :

    def __init__(self, particle = "ENERGY", lun = -22):
        self.particle = particle # WHAT(2) particle or particle family type to be scored
        self.lun = lun # WHAT(3) Logical unit number for output

    def SetMeshCartesian(self, meshType = 0,
                         xmax = 10, ymax = 10, zmax = 10,
                         xmin = -10, ymin = -10, zmin = -10,
                         nx = 20, ny = 20, nz = 20):
        if meshType == 0 or meshType == 10 :
            self.meshType = meshType # WHAT(1) mesh type
        else :
            print("Warning symmetric cartesian mesh type required (meshType=0/10")
            return

        self.xmax = xmax # WHAT(4)
        self.ymax = ymax # WHAT(5)
        self.zmax = zmax # WHAT(6)

        self.xmin = xmin # continuation WHAT(1)
        self.ymin = ymin # continuation WHAT(2)
        self.zmin = zmin # continuation WHAT(3)

        self.nx = nx # continuation WHAT(4)
        self.ny = ny # continuation WHAT(5)
        self.nz = nz # continuation WHAT(6)


    def SetMeshCylindrical(self, meshType = 0,
                           rmax = 10, y = 10, zmax = 10,
                           rmin = 5, x = 10, zmin = -10,
                           nr = 20, np = 20, nz = 20):
        if meshType == 1 or meshType == 11 :
            self.meshType = meshType
        else:
            print("Warning symmetric cylindrical mesh type required (meshType=1/11")
            return

        self.rmax = rmax
        self.y = y
        self.zmax = zmax

        self.rmin = rmin
        self.x = x
        self.zmin = zmin

        self.nr = nr
        self.np = np
        self.nz = nz


    def SetMeshRegion(self, meshType ):
        pass

    def AddTransformation(self): # ROTPRBIN
        pass






