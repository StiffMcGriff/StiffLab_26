from spleeter.separator import Separator

class StemSeparator:
    def __init__(self):
        self.separator = Separator('spleeter:4stems')

    def separate(self, input_path, output_dir):
        self.separator.separate_to_file(
            audio_descriptor=input_path,
            output_path=output_dir
        )
