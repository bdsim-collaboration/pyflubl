import json as _json
import os as _os

def clear_flukarun() :
    _os.system("rm -rf *_pyflubl.root *.err *.log *.out ran* *_dump")

def load_bookkeeping(bookkeeping_file):

    # open file
    with open(bookkeeping_file, "r", encoding="utf-8") as f:

        # load JSON data
        d = _json.load(f)

        return d
