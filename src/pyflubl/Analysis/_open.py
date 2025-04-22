from ._usrbdx import *
from ._usrbin import *

from ._usrdump import *
def openFile(filename, type) :
    fd = open(filename, "rb")

    if type == "usrbdx":
        return Usrbdx(fd)
    elif type == "usrbin":
        return Usrbin(fd)
    elif type == "usrdump":
        return Usrdump(fd)

    fd.close()
