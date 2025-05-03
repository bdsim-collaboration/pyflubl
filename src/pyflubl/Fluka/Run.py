class Rfluka :

    def __init__(self,
                 inp_file
                 dpm=False,
                 executable=None,
                 last_cycle=1,
                 final_cycle=5,
                 max_cpu_time=None,
                 debugger=None,
                 path=None,
                 renice=None):
        self.dpm = dpm
        self.executable = executable
        self.last_cycle = last_cycle
        self.final_cycle = final_cycle
        self.max_cpu_time = max_cpu_time
        self.debugger = debugger
        self.path = path
        self.renice = renice

    def run(self, run_path) :

        # create new path

        # copy over to new path

        # run fluka

        pass

