class Extract_Vocal():
    """
    Using Spleeter, separates a mp3 file into the accompaniment and instrumental parts in a .wav format.
    Test this class individually before running the main process.
    Requires spleeter installed (via pip or other ways) and runnable on cmd terminal.
    """
    def __init__(self, input, output_folder):
        import os

        self.file = input
        self.output_folder = output_folder

        self.file_name = os.path.basename(self.file)
        self.file_name = os.path.splitext(self.file_name)[0]
        return

    def separate(self):
        import subprocess
        
        spleeter_cmd = f'spleeter separate "{self.file}" -p spleeter:2stems -o {self.output_folder}'
        
        print(f"Separating {self.file_name}")
        
        subprocess.run(spleeter_cmd, stderr=subprocess.PIPE, shell=True)
        return

    def get_vocal_path(self, vocals = True):
        from pathlib import Path
        output_folder = self.output_folder + "\\" + self.file_name
        if vocals:
            vocal_file = output_folder + '\\vocals.wav'
        else:
            vocal_file = output_folder + '\\accompaniment.wav'

        if not Path(vocal_file).exists():
            print('Error occured in dissection process. Trying again.')
            self.separate()

        return output_folder, vocal_file

    def delete_folder(self):
        import subprocess
        from pathlib import Path

        folder, _ = self.get_vocal_path()
        if Path(folder).exists():
            subprocess.run(['rd', '/s', '/q', folder], shell=True)
        
        return

"""
Sample usage:

FILE_PATH = "C:\\Users\\yoasobi.mp3"
VOCAL_OUTPUT = "C:\\Users\\Music\\BI\\Separated\\"

separator = Extract_Vocal(FILE_PATH, VOCAL_OUTPUT)
separator.separate()
##separator.delete_folder()

o, _ = separator.get_vocal_path()
print(o)


FILE_PATH = "C:\\Users\\831.mp3"
VOCAL_OUTPUT = "C:\\Users\\Music\\BI\\Separated\\"

separator = Extract_Vocal(FILE_PATH, VOCAL_OUTPUT)
separator.separate()
"""