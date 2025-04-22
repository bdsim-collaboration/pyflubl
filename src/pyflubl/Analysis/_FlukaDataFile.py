from ._fortran import *
import struct as _struct

class FlukaDataFile:
    def __init__(self, fd):
        self.title = None
        self.time = None
        self.weight = None
        self.ncase = None
        self.nbatch = None

        self.read_header(fd)

    def read_header(self, fd):
        data = fortran_read(fd)

        data_size = len(data)

        if data_size == 116:
            (self.title, self.time, self.weight) = _struct.unpack("=80s32sf", data)
            self.ncase = 1
            self.nbatch = 1
        elif data_size == 120:
            (self.title, self.time, self.weight, self.ncase) = _struct.unpack("=80s32sfi", data)
            self.nbatch = 1
        elif data_size == 124:
            (self.title, self.time, self.weight, self.ncase, self.nbatch) = _struct.unpack(
                "=80s32sfii", data
            )
        elif data_size == 128:
            (
                self.title,
                self.time,
                self.weight,
                self.ncase,
                over1b,
                self.nbatch,
            ) = _struct.unpack("=80s32sfiii", data)

    def read_data(self, fd):
        pass

    def print_header(self):
        print("title  : ", self.title)  # noqa: T201
        print("time   : ", self.time)  # noqa: T201
        print("weight : ", self.weight)  # noqa: T201
        print("ncase  : ", self.ncase)  # noqa: T201
        print("nbatch : ", self.nbatch)  # noqa: T201