import glob as _glob

from subprocess import PIPE as _PIPE
from subprocess import Popen as _Popen

class PostProcessing:

    path_to_fluka_bin = "/Users/stewart.boogert/Dropbox/Physics/coderepos/fluka/fluka4-3.0-apple/bin/"

    def __init__(self, input_files, output_file):

        if type(input_files) is str :
            self.input_files = self._makeFileListFromString(input_files)
        elif type(input_files) is list :
            self.input_files = input_files

        self.output_file = output_file

    def _makeFileListFromString(self, input_files):
        return _glob.glob(input_files)

    def run(self, command, debug = False):
        p = _Popen(self.path_to_fluka_bin + "/" + command,
                   stdout=_PIPE, stdin=_PIPE, stderr=None,
                   shell=True, encoding="ascii")

        for file in self.input_files :
            print(command + " : " +file)
            p.stdin.write(file+"\n")
            p.stdin.flush()

            # read 7 lines of output from command
            for i in range(0,7) :
                rl = p.stdout.readline()
                if debug and rl !="\m":
                    print(rl.strip())

        p.stdin.write("\n")
        p.stdin.flush()

        p.stdin.write(self.output_file + "\n")
        p.stdin.flush()

        p.communicate()