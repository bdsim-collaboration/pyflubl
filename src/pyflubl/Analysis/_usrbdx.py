from ._FlukaDataFile import FlukaDataFile as _FlukaDataFile
from ._fortran import *
import struct as _struct
import numpy as _np

class FlukaBdxData:
    def __init__(self, index, name, type):
        self.index = index
        self.name = name
        self.type = type

class Usrbdx(_FlukaDataFile):
    def __init__(self, file):

        self.fd = fd
        self.detector = []

        if type(file) is str:
            fd = open(file, "rb")
        else:
            fd = file
            fd.seek(0)

        super().read_header(fd)
        self.read_file(fd)

    def read_file(self, fd):
        while self.read_header(fd):
            self.read_data(fd)

        self.read_stats(fd)

    def read_data(self, fd):
        self.detector[-1].data = _np.reshape(
            _np.frombuffer(fortran_read(fd), _np.float32),
            (self.detector[-1].ne, self.detector[-1].na),
            order="F",
        )

    def read_stats(self, fd):
        data = fortran_read(fd)
        if data is None:
            print("No statistics")
            return

        if len(data) == 14 and data[0:10] == b"STATISTICS":
            self.stat_pos = fd.tell()

        # 6 data records
        # 0 : total, error
        # 1 :

        for det in self.detector:
            data = fortran_read(fd)

            data = _struct.unpack(f"={len(data) // 4}f", data)
            det.total = data[0]
            det.totalError = data[1]

            det.error = []
            for i in range(6):
                data = fortran_read(fd)
                det.error.append(_struct.unpack(f"={len(data) // 4}f", data))

    def read_header(self, fd):
        pos = fd.tell()

        data = fortran_read(fd)
        if not data:
            return False

        if len(data) != 78:
            fd.seek(pos)  # return to statistics
            return False

        header = _struct.unpack("=i10siiiifiiiffifffif", data)

        num = header[0]
        name = header[1]
        type = header[2]

        fluka_data = FlukaBdxData(num, name, type)

        fluka_data.dist = header[3]
        fluka_data.reg1 = header[4]
        fluka_data.reg2 = header[5]
        fluka_data.area = header[6]
        fluka_data.twoway = header[7]
        fluka_data.fluence = header[8]
        fluka_data.lowneu = header[9]
        fluka_data.elow = header[10]
        fluka_data.ehigh = header[11]
        fluka_data.ne = header[12]
        fluka_data.de = header[13]
        fluka_data.alow = header[14]
        fluka_data.ahigh = header[15]
        fluka_data.na = header[16]
        fluka_data.da = header[17]

        self.detector.append(fluka_data)

        return True

    def __del__(self):
        self.fd.close()