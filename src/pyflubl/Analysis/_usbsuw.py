from ._PostProcessing import PostProcessing as _PostProcessing

class Usbsum(_PostProcessing):
    def __init__(self, input_files, output_file) :
        super().__init__(input_files=input_files, output_file=output_file)


    def run(self, debug=False):
        super().run(command="usbsuw", debug=debug)


