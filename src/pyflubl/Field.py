import numpy as _np
from .Fluka import Mgndata as _Mgndata
from .Fluka import Mgncreat as _Mgncreat

from numpy.typing import NDArray

class Field(object):
    def __init__(self,
                 array   : NDArray = None,
                 columns : list[str] = None,
                 name    : str = "field") :
        self.name            = name
        self.data = _np.array([]) if array is None else  array
        self.columns = [] if columns is None else columns
        self.header          = {}
        self.nDimensions     = 0
        self.comments        = []

class Field2D(Field) :
    """
    Utility class to write a 2D field map array to FLUKA input field format.

    The array supplied should be 3 dimensional. Dimensions are:
    (x,y,value) where value has 5 elements [x,y,fx,fy,fz].  So a 100x50 (x,y)
    grid would have np.shape of (100,50,5).

    Example::

    >>> a = Field2D(data) # data is a prepared array
    >>> a.Write('outputFileName.inp')
    """


    def __init__(self, data, firstColumn='X', secondColumn='Y', name = "field") :

        if data.shape[2] != 5 :
            raise IndexError("The array supplied should be 3 dimensional, dimension 3 should be 5 long")
        columns = [firstColumn, secondColumn, 'Fx', 'Fy', 'Fz']
        super(Field2D, self).__init__(data, columns, name)
        inds = [0, 1]

        fcl = firstColumn.lower() # first column
        scl = secondColumn.lower() # second column

        self.header[fcl+'min'] = _np.min(self.data[:,:,0])
        self.header[fcl+'max'] = _np.max(self.data[:,:,0])
        self.header['n'+fcl]   = _np.shape(self.data)[inds[0]]
        self.header[scl+'min'] = _np.min(self.data[:,:,1])
        self.header[scl+'max'] = _np.max(self.data[:,:,1])
        self.header['n'+scl]   = _np.shape(self.data)[inds[1]]
        self.nDimensions = 2

        self.resample = False
        self.cards = []


    def Resample(self, newXPoints : int, newYPoints : int, method : str = "linear") :
        from scipy.interpolate import RegularGridInterpolator

        if  self.resample :
            raise ValueError("Resampling is only possible once")

        f = self.data[:,:,2:]

        x = _np.linspace(self.header[f"{self.columns[0].lower()}min"],
                         self.header[f"{self.columns[0].lower()}max"],
                         self.header[f"n{self.columns[0].lower()}"])
        y = _np.linspace(self.header[f"{self.columns[1].lower()}min"],
                         self.header[f"{self.columns[1].lower()}max"],
                         self.header[f"n{self.columns[1].lower()}"])

        xi = _np.linspace(self.header[f"{self.columns[0].lower()}min"],
                          self.header[f"{self.columns[0].lower()}max"],
                          newXPoints)
        yi = _np.linspace(self.header[f"{self.columns[1].lower()}min"],
                          self.header[f"{self.columns[1].lower()}max"],
                          newYPoints)

        self.f_interpolator = RegularGridInterpolator((x, y), f, method=method)

        xd = self.data[:,:,0]
        yd = self.data[:,:,1]

        xmg, ymg = _np.meshgrid(xi, yi)

        b_inter = self.f_interpolator((xmg.flatten(), ymg.flatten())).transpose()
        self.data = _np.vstack((xmg.flatten(), ymg.flatten(), b_inter[0], b_inter[1], b_inter[2])).transpose()

        self.header['nx'] = newXPoints
        self.header['ny'] = newYPoints

        # Mark data has been resampled
        self.resample = True

    def Plot(self):
        import matplotlib.pyplot as plt

        xk = self.columns[0].lower()
        yk = self.columns[1].lower()

        d = self.data.reshape((self.header[f"n{xk}"], self.header[f"n{yk}"], 5))
        b = _np.sqrt(d[:, :, 2] ** 2 + d[:, :, 3] ** 2 + d[:, :, 4] ** 2)
        plt.imshow(b)
        plt.colorbar()

    def MakeCards(self):
        self.cards = []

        self.cards.append(_Mgncreat(_Mgncreat.INTERPOLATED,
                                    sdum=self.name,
                                    nxr_pts = self.header[f"n{self.columns[0].lower()}"],
                                    ny_pts  = self.header[f"n{self.columns[1].lower()}"],
                                    xr_min  = self.header[f"{self.columns[0].lower()}min"],
                                    xr_max  = self.header[f"{self.columns[0].lower()}max"],
                                    y_min   = self.header[f"{self.columns[1].lower()}min"],
                                    y_max   = self.header[f"{self.columns[1].lower()}max"]))

        for d in self.data.reshape(-1,5) :
            self.cards.append(_Mgndata(d[2], d[3], d[4], sdum=self.name))

    def Write(self, fileName : str):

        # make cards
        if self.cards == []:
            self.MakeCards()

        # write to file
        with open(fileName, 'w') as f:
            for c in self.cards :
                f.write(c.toFreeString()+"\n")