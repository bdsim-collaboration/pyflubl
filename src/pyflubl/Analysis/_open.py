from ._usrbdx import *
from ._usrbin import *
from ._usrdump import *
import json as _json

def openFile(filename, type) :
    fd = open(filename, "rb")

    if type == "usrbdx":
        return Usrbdx(fd)
    elif type == "usrbin":
        return Usrbin(fd)
    elif type == "usrdump":
        return Usrdump(fd)

    fd.close()

def openBookkeepingFile(filename) :
    with open(filename, 'r') as f:
        d =  _json.load(f)

        # convert integer keys back from str to int
        d['regionnumber_regionname'] = {int(k): v for k, v in d['regionnumber_regionname'].items()}
        d['usrbinnumber_usrbininfo'] = {int(k): v for k, v in d['usrbinnumber_usrbininfo'].items()}

        return d