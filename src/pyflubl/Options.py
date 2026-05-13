class Options:

    def __init__(self):

        # vacuum
        self._vacuumMaterial = "VACUUM"

        # beampipe
        self._beampipeMaterial = "IRON"
        self._beampipeThickness = 5
        self._beampipeRadius = 50

        # outer
        self._outerMaterial = "AIR"
        self._outerHorizontalSize = 1000
        self._outerVerticalSize = 1000

        # world material
        self._worldMaterial = "AIR"

        # jcol defaults

        # jcoltip defaults


        # sampler
        self._samplerMaterial = "VACUUM"
        self._samplerLength = 1e-6
        self._samplerDiameter = 2000

    @property
    def vacuumMaterial(self):
        return self._vacuumMaterial

    @vacuumMaterial.setter
    def vacuumMaterial(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._vacuumMaterial = value

    @property
    def beampipeMaterial(self):
        return self._beampipeMaterial

    @beampipeMaterial.setter
    def beampipeMaterial(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._beampipeMaterial = value

    @property
    def beampipeThickness(self):
        return self._beampipeThickness

    @beampipeThickness.setter
    def beampipeThickness(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._beampipeThickness = value

    @property
    def beampipeRadius(self):
        return self._beampipeRadius

    @beampipeRadius.setter
    def beampipeRadius(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._beampipeRadius = value

    @property
    def outerMaterial(self):
        return self._outerMaterial

    @outerMaterial.setter
    def outerMaterial(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._outerMaterial = value

    @property
    def outerHorizontalSize(self):
        return self._outerHorizontalSize

    @outerHorizontalSize.setter
    def outerHorizontalSize(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._outerHorizontalSize = value

    @property
    def outerVerticalSize(self):
        return self._outerVerticalSize

    @outerVerticalSize.setter
    def outerVerticalSize(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._outerVerticalSize = value

    @property
    def worldMaterial(self):
        """Getter method"""
        return self._worldMaterial

    @worldMaterial.setter
    def worldMaterial(self, value):
        """Setter method"""
        if not value:
            raise ValueError("Name cannot be empty")
        self._worldMaterial = value

    @property
    def samplerMaterial(self):
        """Getter method"""
        return self._samplerMaterial

    @samplerMaterial.setter
    def samplerMaterial(self, value):
        """Setter method"""
        if not value:
            raise ValueError("Name cannot be empty")
        self._samplerMaterial = value

    @property
    def samplerLength(self):
        """Getter method"""
        return self._samplerLength

    @samplerLength.setter
    def samplerLength(self, value):
        """Setter method"""
        if not value:
            raise ValueError("Name cannot be empty")
        self._samplerLength = value

    @property
    def samplerDiameter(self):
        return self._samplerDiameter

    @samplerDiameter.setter
    def samplerDiameter(self, value):
        """Setter method"""
        if not value:
            raise ValueError("Name cannot be empty")
        self._samplerDiameter = value

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