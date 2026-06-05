try :
    import ROOT as _ROOT
except ImportError :
    print("ROOT not found")

try :
    import uproot as _uproot
except ImportError :
    print("uproot not found")

import numpy as _np
import xarray as _xr
import pandas as _pd
import awkward as _ak

from scipy.spatial.transform import Rotation as _Rotation
from scipy.ndimage import affine_transform as _affine_transform

from ..Coordinates import Coordinates as _Coordinates
from ._open import openFile as _openFile
from ._plot import plot_coordinates_projection as _plot_coordinates_projection
from ._plot import plot_usrbin_projection_xarray as _plot_usrbin_projection_xarray
from ._plot import plot_usrdump as _plot_usrdump

class PyflublOutput:

    def __init__(self,
                 jsonFileName = None,
                 jsonCoordinateFileName = None,
                 dumpFileName = None,
                 rootFileName = None,
                 usrbinFileName = None,
                 usrbnxFileName = None):

        self.dumpFile = None
        self.usrbinFile = None
        self.uprootTree = None

        if jsonFileName is not None:
            self.bookkeeping = load_bookkeeping(jsonFileName)
        if jsonCoordinateFileName is not None:
            self.coordinates = load_coorinates(jsonCoordinateFileName)
        if dumpFileName is not None:
            self.dumpFile = _openFile(dumpFileName,"usrdump")
        if rootFileName is not None:
            uprootFile = _uproot.open(rootFileName)
            self.uprootTree = uprootFile["event"]
            # self.rootPandas = uprootTree.array(library="pd")
        if usrbinFileName is not None:
            self.usrbinFile = _openFile(usrbinFileName,"usrbin")

    def get_sampler_names(self):
        return list(self.bookkeeping['samplernames_samplernumber'].keys())

    def get_sampler(self, name):
        samplerdata_dict = {}
        samplerdata_dict['x'] = _np.array(_ak.flatten(self.uprootTree[name+'.x'].array(library="ak")))
        samplerdata_dict['y'] = _np.array(_ak.flatten(self.uprootTree[name+'.y'].array(library="ak")))
        #samplerdata_dict['z'] = _np.array(_ak.flatten(self.uprootTree[name+'.z'].array(library="ak")))
        samplerdata_dict['xp'] = _np.array(_ak.flatten(self.uprootTree[name+'.xp'].array(library="ak")))
        samplerdata_dict['yp'] = _np.array(_ak.flatten(self.uprootTree[name+'.yp'].array(library="ak")))
        samplerdata_dict['zp'] = _np.array(_ak.flatten(self.uprootTree[name+'.zp'].array(library="ak")))
        samplerdata_dict['partID'] = _np.array(_ak.flatten(self.uprootTree[name+'.partID'].array(library="ak")))
        samplerdata_dict['T'] = _np.array(_ak.flatten(self.uprootTree[name+'.T'].array(library="ak")))
        samplerdata_dict['energy'] = _np.array(_ak.flatten(self.uprootTree[name+'.energy'].array(library="ak")))

        return _pd.DataFrame(samplerdata_dict)

    def get_eloss(self) :
        elossdata_dict = {}
        elossdata_dict['E'] = _np.array(_ak.flatten(self.uprootTree['eloss.E'].array(library="ak")))
        elossdata_dict['S'] = _np.array(_ak.flatten(self.uprootTree['eloss.S'].array(library="ak")))

        return  _pd.DataFrame(elossdata_dict)

    def plot_projection(self,
                        projection = "zx",
                        eventNumber = 0,
                        detector = None):
        ax = None
        xlim = None
        ylim = None

        if self.coordinates is not None:
            ax = _plot_coordinates_projection(self.coordinates, projection=projection,
                                              plotCoordinateMarkers=False,
                                              plotNormals=False,
                                              plotFilledElements=False)
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

        if self.dumpFile is not None:
            if type(eventNumber) is int :
                if eventNumber >= 0 :
                    self.dumpFile.read_event(eventNumber)
                    _plot_usrdump(self.dumpFile,projection=projection)
            elif type(eventNumber) is slice :
                for i in range(eventNumber.start, eventNumber.stop,1) :
                    self.dumpFile.read_event(i)
                    _plot_usrdump(self.dumpFile, projection=projection)

        if self.usrbinFile is not None and detector is not None:
            self.usrbinXArray = []

            for idet, det in enumerate(self.usrbinFile.detector) :

                # detector xarray
                det_xr = userbin_make_xarray(det)

                # store xarray for later
                self.usrbinXArray.append(det_xr)

                # detector info
                det_info = self.bookkeeping['usrbinnumber_usrbininfo'][str(idet)] # detector is string because of JSON loading

                rotation = _np.array(det_info['rotation'])
                translation = _np.array(det_info['translation'])
                #print(f'idef={idet}')
                #print(f'det_info[rotation]={rotation}')
                #print(f'det_info[translation]={translation}')

                # plot xarray
                _plot_usrbin_projection_xarray(det_xr,
                                               projection=projection,
                                               rotation_matrix=det_info['rotation'],
                                               translation_vector=det_info['translation'])

                # reset axis scales
                if xlim is not None:
                    ax.set_xlim(xlim)
                    ax.set_ylim(ylim)

        return ax

def load_bookkeeping(file_name) :
    import json
    with open(file_name, "r") as f :
        bookkeeping = json.load(f)
    return bookkeeping

def load_coorinates(file_name):
    c = _Coordinates()
    c.LoadJSON(file_name)
    return c

def userbin_make_xarray(detector) :

    xr = _xr.DataArray(detector.data,
                       dims=['x','y','z'],
                       coords={
                           "x": _np.linspace(detector.e1low*10, detector.e1high*10, detector.e1n),
                           "y": _np.linspace(detector.e2low*10, detector.e2high*10, detector.e2n),
                           "z": _np.linspace(detector.e3low*10, detector.e3high*10, detector.e3n)})

    return xr

def transform_xarray(xarray,
                     rotation= _np.array([[1,0,0],[0,1,0],[0,0,1]]),
                     translation = _np.array([0,0,0])) :

    x = _np.array(xarray.coords['x'])
    y = _np.array(xarray.coords['y'])
    z = _np.array(xarray.coords['z'])

    #xp = rotation[0,0] * x + rotation[0,1] * y + rotation[0,2] * z + translation[0]
    #yp = rotation[1,0] * x + rotation[1,1] * y + rotation[1,2] * z + translation[1]
    #zp = rotation[2,0] * x + rotation[2,1] * y + rotation[2,2] * z + translation[2]

    xp = x + translation[0]
    yp = y + translation[1]
    zp = z + translation[2]

    xarray.coords['x'] = xp
    xarray.coords['y'] = yp
    xarray.coords['z'] = zp



