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
        if array is None :
            self.data = _np.array([])
        if columns is None :
            self.columns = columns

        self.data            = array
        self.columns         = columns
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
            raise IndexError("The array supplied should be 3 dimensional, dimension 3 shoud be 5 long")
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

        self.cards = []

    def Resample(self, newXPoints : int, newYPoints : int) :
        from scipy.interpolate import RegularGridInterpolator

        f = self.data[:,:,2:]

        x = _np.linspace(self.header['xmin'], self.header['xmax'], self.header['nx'])
        y = _np.linspace(self.header['ymin'], self.header['ymax'], self.header['ny'])

        xi = _np.linspace(self.header['xmin'], self.header['xmax'], newXPoints)
        yi = _np.linspace(self.header['ymin'], self.header['ymax'], newYPoints)
        self.f_interpolator = RegularGridInterpolator((x, y), f, method="cubic")

        xd = self.data[:,:,0]
        yd = self.data[:,:,1]

        xmg, ymg = _np.meshgrid(xi, yi)

        b_inter = self.f_interpolator((xmg.flatten(), ymg.flatten())).transpose()
        self.data = _np.vstack((xmg.flatten(), ymg.flatten(), b_inter[0], b_inter[1], b_inter[2])).transpose()

        self.header['nx'] = newXPoints
        self.header['ny'] = newYPoints

    def Plot(self):
        import matplotlib.pyplot as plt
        d = self.data.reshape((self.header['nx'], self.header['nx'], 5))
        b = _np.sqrt(d[:, :, 2] ** 2 + d[:, :, 3] ** 2 + d[:, :, 4] ** 2)
        plt.imshow(b)
        plt.colorbar()

    def MakeCards(self):
        self.cards = []

        self.cards.append(_Mgncreat(_Mgncreat.INTERPOLATED,
                                    sdum=self.name,
                                    nxr_pts = self.header['nx'],
                                    ny_pts = self.header['ny'],
                                    xr_min = self.header['xmin'],
                                    xr_max = self.header['xmax'],
                                    y_min = self.header['ymin'],
                                    y_max = self.header['ymax']))

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