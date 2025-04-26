from ._FlukaDataFile import FlukaDataFile as _FlukaDataFile
from ._fortran import *
import struct as _struct
import numpy as _np

def debugDumpFile(fd, limit=10000000):
    fd.seek(0)

    iData = 0
    data = True

    while data:
        data = fortran_read(fd)
        if data and iData < limit:
            print(iData, len(data))  # noqa: T201
        iData += 1

    print("total records", iData)  # noqa: T201

class Usrdump(_FlukaDataFile):
    def __init__(self, fd, iEventHeaderToRead=10000):

        self.fd = fd

        self.event_seek = []
        self.read_structure(fd, iEventHeaderToRead)

        self.track_data = []
        self.energy_data = []
        self.source_data = []

    def read_structure(self, fd, iEventHeaderToRead=10000):
        print("read_header")

        # start of file
        fd.seek(0)

        # count of file records
        iRecord = 0
        iEvent = 0

        while True:
            # file position for later recording
            file_pos = fd.tell()

            # read file record
            data = fortran_read(fd)

            # if nothing is read break loop
            if not data:
                break

            # entry header
            if len(data) == 20:
                ndum, mdum, jdum, edum, wdum = _struct.unpack("=iiiff", data)

                # print(ndum, mdum, jdum, edum, wdum)
                if ndum < 0:
                    print(iRecord, file_pos, "read source")
                    self.event_seek.append(file_pos)
                    if iEvent > iEventHeaderToRead:
                        break

                    iEvent += 1
                    iRecord += 1

                # skip data
                fortran_read(fd)

        self.event_seek.append(100000000000)

    def read_event(self, ievent=0):
        print("read_event")
        # clear event data
        self.track_data.clear()
        self.energy_data.clear()
        self.source_data.clear()

        # check event number
        if ievent > len(self.event_seek) - 1:
            print("Event out of range")
            return

        # move to start of event
        self.fd.seek(self.event_seek[ievent])

        # read header
        while True:
            if self.fd.tell() == self.event_seek[ievent + 1]:
                print("next event reached", self.fd.tell())
                break

            # read file record
            data = fortran_read(self.fd)

            # break on no data
            if not data:
                break

            if len(data) == 20:
                ndum, mdum, jdum, edum, wdum = _struct.unpack("=iiiff", data)

                # tracking
                if ndum > 0:
                    ntrack = ndum
                    mtrack = mdum
                    jtrack = jdum
                    etrack = edum
                    wtrack = wdum
                    data = fortran_read(self.fd)
                    data = list(_struct.unpack(f"={3 * (ntrack + 1) + mtrack + 1}f", data))
                    self.track_data.append(data)
                # energy
                elif ndum == 0:
                    icode = ndum
                    jtrack = jdum
                    etrack = edum
                    wtrack = wdum
                    data = fortran_read(self.fd)
                    data = list(_struct.unpack("=4f", data))
                    self.energy_data.append(data)
                # source
                else:
                    ncase = ndum
                    npflka = mdum
                    nstmax = jdum
                    tkesum = edum
                    weipri = wdum
                    data = fortran_read(self.fd)
                    data = list(_struct.unpack("=" + ("i8f" * npflka), data))
                    self.source_data.append(data)

    def trackDataToPolydata(self):
        import vtk as _vtk

        vp = _vtk.vtkPoints()
        ca = _vtk.vtkCellArray()
        pd = _vtk.vtkPolyData()

        iPnt = 0
        for t in self.track_data:
            iPntStart = iPnt
            id1 = vp.InsertNextPoint(10 * t[0], 10 * t[1], 10 * t[2])
            id2 = vp.InsertNextPoint(10 * t[3], 10 * t[4], 10 * t[5])

            iPnt += 2

            ca.InsertNextCell(2)
            ca.InsertCellPoint(id1)
            ca.InsertCellPoint(id2)

        pd.SetPoints(vp)
        pd.SetLines(ca)

        return pd

    def __del__(self):
        self.fd.close()