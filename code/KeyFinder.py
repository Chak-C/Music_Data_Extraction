import librosa
import numpy as np

class Key_Finder():
    def __init__(self, y, sr, harmonic=False):
        """
        Predictions begin upon object creation.
        Turn harmonics off for faster runtime. 
            librosa hpss model is called to separate harmonics and percussive if turned on.
            (which is not needed if a vocal wav/mp3 is used as input)
        
        Use get_key(self) or print_key(self) to retrieve keys.
        """
        self.y = y
        self.sr = sr
        self.harmonic = harmonic

        if harmonic:
            y_harmonic, _ = librosa.effects.hpss(y)
            self.y = y_harmonic

        chroma_to_key = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
        key_list = [chroma_to_key[i] + ' major' for i in range(12)] + [chroma_to_key[i] + ' minor' for i in range(12)]
        
        # Krumhansl-Kessler key pofile
        major_profile = [6.35, 2.23, 3.58, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

        # Chroma Energy Normalized Statistics (chroma_cens) for music classification
        # can use CQT or VQT but hold off from STFT unless runtime is a concern 
        self.chromograph = librosa.feature.chroma_cens(y=y,sr=sr,bins_per_octave=24)
        
        self.chromo_vals = []

        for i in range(12):
            self.chromo_vals.append(np.sum(self.chromograph[i]))

        # number of keys present in the y
        self.keyfreqs = {chroma_to_key[i]: self.chromo_vals[i] for i in range(12)}
        
        #print(self.keyfreqs)
        #{'C': 3400.2705, 'C#': 4598.6323, 'D': 3689.142, 'D#': 3358.1611, 'E': 3651.1636, 'F': 4995.2744, 'F#': 6058.3125, 'G': 4546.5664, 'G#': 4586.827, 'A': 4149.5166, 'A#': 4395.574, 'B': 3649.0479}#
        self.major_cor = []
        self.minor_cor = []

        for i in range(12):
            key_test = [self.keyfreqs.get(chroma_to_key[(i+j)%12]) for j in range(12)]
            self.major_cor.append(round(np.corrcoef(major_profile, key_test)[1,0],3))
            self.minor_cor.append(round(np.corrcoef(minor_profile, key_test)[1,0],3))

        self.music_keys = {}
        for i in range(12):
            self.music_keys[key_list[i]] = self.major_cor[i]
            self.music_keys[key_list[i+12]] = self.minor_cor[i]

        self.pred_key = max(self.music_keys, key=self.music_keys.get)
        return
    
    def get_key(self): return self.pred_key
    
    def print_key(self, message = ''):
        print(f'{message}Predicted key: ', self.pred_key)

"""
Example usage:

FILE_PATH = "C:\\Users\\output\\attention.mp3"

y, sr = librosa.load(FILE_PATH, sr = None, mono = True)

attention = Key_Finder(y, sr, harmonics=True)
attention.print_key()
"""
