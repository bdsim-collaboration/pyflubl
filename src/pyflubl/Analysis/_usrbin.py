from ._FlukaDataFile import FlukaDataFile as _FlukaDataFile
from ._fortran import *
import struct as _struct
import numpy as _np

class FlukaBinData:
    def __init__(self, index, name, type):
        self.index = index
        self.name = name
        self.type = type
        self.data = None
        self.stats = None

    def binToVtkGrid(self):
        import vtk as _vtk
        import vtk.util.numpy_support as _numpy_support

        # rectilinear
        if self.mesh == 0:
            imdata = _vtk.vtkImageData()
            dataArray = _numpy_support.numpy_to_vtk(
                _np.log10(self.data.ravel()), deep=True, array_type=_vtk.VTK_DOUBLE
            )

            print(_np.log10(self.data.ravel()).min(), _np.log10(self.data.ravel()).max())
            ox = -(self.e1high - self.e1low) / 2 * 10
            oy = -(self.e2high - self.e2low) / 2 * 10
            oz = -(self.e3high - self.e3low) / 2 * 10
            print("origin", ox, oy, oz)
            dx = (self.e1high - self.e1low) / self.e1n * 10
            dy = (self.e2high - self.e2low) / self.e2n * 10
            dz = (self.e3high - self.e3low) / self.e3n * 10

            imdata.SetDimensions(self.data.shape)
            imdata.SetSpacing([dx, dy, dz])
            imdata.SetOrigin([ox, oy, oz])
            imdata.GetPointData().SetScalars(dataArray)

            return imdata

        # cylindrical
        elif self.mesh == 1:
            pass

class Usrbin(_FlukaDataFile):
    def __init__(self, fd, read_data=False):

        self.fd = fd

        fd.seek(0)

        self.stat_pos = -1

        self.detector = []

        super().read_header(fd)
        self.read_file(fd)

    def read_file(self, fd):
        while self.read_header(fd):
            self.read_data(fd)
        print(f"Read {len(self.detector)} detectors")

        self.read_stats(fd)

    def read_data(self, fd):
        self.detector[-1].data = _np.reshape(
            _np.frombuffer(fortran_read(fd), _np.float32),
            (self.detector[-1].e1n, self.detector[-1].e2n, self.detector[-1].e3n),
            order="F",
        )

    def read_stats(self, fd):
        data = fortran_read(fd)
        if data is None:
            print("No statistics")
            return

        if len(data) == 14 and data[0:10] == b"STATISTICS":
            self.stat_pos = fd.tell()

        print("Statistics present")
        for det in self.detector:
            data = fortran_read(fd)
            det.errors = _np.reshape(
                _np.frombuffer(data, _np.float32), (det.e1n, det.e2n, det.e3n), order="F"
            )

    def read_header(self, fd):
        pos = fd.tell()
        data = fortran_read(fd)

        if data is None:
            return False

        if len(data) != 86:
            fd.seek(pos)  # return to statistics
            return False

        # Parse header
        header = _struct.unpack("=i10siiffifffifffififff", data)

        idet = header[0]
        name = str(header[1]).replace("'", "").strip(" ")
        mesh = int(header[2])
        e1low = float(header[4])
        e1high = float(header[5])
        e1n = int(header[6])
        e1d = float(header[7])

        e2low = float(header[8])
        e2high = float(header[9])
        e2n = int(header[10])
        e2d = float(header[11])

        e3low = float(header[12])
        e3high = float(header[13])
        e3n = int(header[14])
        e3d = float(header[15])

        # print(e1low, e1high, e1n, e1d)
        # print(e2low, e2high, e2n, e2d)
        # print(e3low, e3high, e3n, e3d)

        data_size = e1n * e2n * e3n * 4

        fluka_data = FlukaBinData(idet, name, "bin")

        fluka_data.ncase = self.ncase
        fluka_data.nbatch = self.nbatch
        fluka_data.weight = self.weight
        fluka_data.mesh = mesh

        fluka_data.e1low = e1low
        fluka_data.e1high = e1high

        fluka_data.e2low = e2low
        fluka_data.e2high = e2high

        fluka_data.e3low = e3low
        fluka_data.e3high = e3high

        fluka_data.e1n = e1n
        fluka_data.e2n = e2n
        fluka_data.e3n = e3n

        self.detector.append(fluka_data)

        return True

    def print_header(self):
        super().print_header()

    def __del__(self):
        self.fd.close()