class Options:

    def __init__(self):

        self.vacuumMaterial = "VACUUM"

        self.beampipeMaterial = "IRON"
        self.beampipeThickness = 5
        self.beampipeRadius = 100

        self.outerMaterial = "AIR"
        self.outerHorizontalSize = 200
        self.outerVerticalSize = 200


    def __repr__(self):
        s = "Options\n"

        s+= "beampipe\n"
        s+= "========\n"
        s+= "vacuumMaterial: " + self.vacuumMaterial + "\n"
        s+= "beampipeMaterial: " + self.beampipeMaterial + "\n"
        s+= "beampipeThickness: " + str(self.beampipeThickness) + "\n"
        s+= "beampipeRadius: " + str(self.beampipeRadius) + "\n"

        s+= "Outer\n"
        s+= "=====\n"
        s+= "outerMaterial: " + self.outerMaterial + "\n"
        s+= "outerHorizontalSize: " + str(self.outerHorizontalSize) + "\n"
        s+= "outerVerticalSize: " + str(self.outerVerticalSize) + "\n"

        return s