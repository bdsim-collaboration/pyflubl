import struct as _struct

def fortran_skip(f):
    rlen = f.read(4)

    if not rlen:
        return 0
    (size,) = _struct.unpack("=i", rlen)
    f.seek(size, 1)
    rlen2 = f.read(4)
    if rlen != rlen2:
        msg = "kipping fortran blocks"
        raise OSError(msg)
    return size


def fortran_read(f):
    rlen = f.read(4)
    if not rlen:
        return None
    (size,) = _struct.unpack("=i", rlen)
    data = f.read(size)
    rlen2 = f.read(4)
    if rlen != rlen2:
        msg = "reading fortran"
        raise OSError(msg)
    return data
