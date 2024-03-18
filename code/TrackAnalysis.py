import numpy as np
from scipy.io import wavfile as wav
import numpy as np
import tqdm
import csv

class Track_Analysis():
    """
    Gives a general perspective of note ranges.
    Not accurate though, speculated reasons include:
        My vocal separation process is not distinctive and clear enough.
        Spectrogram is very sensitive to noise at high frequencies.
            - (Attempted to apply gaussian normalization on the mode frequency of the spectrogram to reduce noise at higher ends)
        Ranges of vocal frequencies too broad without pre-distinguishing/told:
            - Variables include: 
                - Track style (jazz, pop, rap, opera etc.)
                - Artist gender (Male, Female, Dual, Mixed, Choir, Instrumental etc.)
                - Artists' expected vocal ranges and potential harminizations
                and more...
            - This analysis is used to perform a (very) general analysis on a track's musical features
                further investigation / paramatization will be needed to improve note detection accuracy
        This class counts frequency frames, NOT actual musical notes:
            - Counting the notes require more computation which makes it difficult to justify its use
                on 100+ tracks.
            - A moving frame (Hanning moving window) is used to count the duration of notes in a track,
                which can be retrieved by [final count] / [FPS].
    
    Assumptions: Works best on wav file without much noise (like vocals or orchestra), 
            The class will only record notes with above 20% max magnitude (changable).
    """
    def __init__(self, vocal_wav):
        self.FPS = 30
        self.FFT_WINDOW_SECONDS = 0.25 # how many seconds of audio make up an FFT window

        # Note range to display
        self.FREQ_MIN = 65 #C2
        self.FREQ_MAX = 856 #A5, tune 2000 for B6, 1000 for B5

        # Threshold to count frame as having notes and not noise
        self.threshold = 0.2

        # Notes to detect
        self.NOTES_DETECTED = 3

        # Note list
        self.NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        # Output (IF NEEDED)

        # Load wav
        self.rate, data = wav.read(vocal_wav)
        self.audio = data.T[0]
        self.FRAME_STEP = (self.rate / self.FPS) # audio samples per video frame
        self.FFT_WINDOW_SIZE = int(self.rate * self.FFT_WINDOW_SECONDS)
        self.AUDIO_LENGTH = len(self.audio)/self.rate

        self.xf = np.fft.rfftfreq(self.FFT_WINDOW_SIZE, 1/self.rate)
        self.FRAME_COUNT = int(self.AUDIO_LENGTH*self.FPS)
        self.FRAME_OFFSET = int(len(self.audio)/self.FRAME_COUNT)

        # Hanning window function
        self.window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, self.FFT_WINDOW_SIZE, False)))

        # Note dictionary tempate
        self.note_frames = {"C2":0, "C#2":0, "D2":0, "D#2":0, "E2":0, "F2":0, "F#2":0, "G2":0, "G#2":0, "A2":0, "A#2":0, "B2":0,
                       "C3":0, "C#3":0, "D3":0, "D#3":0, "E3":0, "F3":0, "F#3":0, "G3":0, "G#3":0, "A3":0, "A#3":0, "B3":0,
                       "C4":0, "C#4":0, "D4":0, "D#4":0, "E4":0, "F4":0, "F#4":0, "G4":0, "G#4":0, "A4":0, "A#4":0, "B4":0,
                       "C5":0, "C#5":0, "D5":0, "D#5":0, "E5":0, "F5":0, "F#5":0, "G5":0, "G#5":0, "A5":0, "A#5":0, "B5":0,
                       "C6":0, "C#6":0, "D6":0, "D#6":0, "E6":0}
        self.keys = list(self.note_frames.keys())
        pass
    
    # See https://newt.phys.unsw.edu.au/jw/notes.html
    def freq_to_number(self, f): return 69 + 12*np.log2(f/440.0)
    def number_to_freq(self, n): return 440 * 2.0**((n-69)/12.0)
    def note_name(self, n): return self.NOTE_NAMES[n % 12] + str(int(n/12 - 1))

    def extract_sample(self, audio, frame_number):
        end = frame_number * self.FRAME_OFFSET
        begin = int(end - self.FFT_WINDOW_SIZE)

        if end == 0:
            # No audio, return all zero
            return np.zeros((np.abs(begin)), dtype=float)
        elif begin<0:
            return np.concatenate([np.zeros((np.abs(begin)), dtype=float), audio[0:end]])
        else:
            return audio[begin:end]
    
    def find_top_notes(self, fft, num, threshold):
        if np.max(fft.real)<threshold:
            return []
        
        lst = [x for x in enumerate(fft.real)]
        lst = sorted(lst, key=lambda x: x[1], reverse=True)

        idx = 0
        found = []
        found_note = set()
        while( (idx<len(lst)) and (len(found)<num)):
            if lst[idx][1] < self.threshold:
                idx += 1
                continue

            if self.xf[lst[idx][0]] <= self.FREQ_MIN:
                idx += 1
                continue

            f = self.xf[lst[idx][0]]    # frequency
            y = lst[idx][1]             # magnitude
            n = self.freq_to_number(f)  # Octive of key, unrounded
            
            n0 = int(round(n))

            name = self.note_name(n0)

            if name not in found_note and f < self.FREQ_MAX:
                found_note.add(name)
                s = [f,self.note_name(n0),y]
                found.append(s)
            idx += 1
        
        return found
    
    def max_amp(self):
        mx = 0
        for frame in range(self.FRAME_COUNT):
            sample = self.extract_sample(self.audio, frame)
            
            fft = np.fft.rfft(sample*self.window)
            fft = np.abs(fft).real
            mx = max(np.max(fft), mx)
        return mx
    
    def create_note_array(self):
        mx = self.max_amp()
        self.all_notes = []
        for frame in tqdm.tqdm(range(self.FRAME_COUNT)):
            sample = self.extract_sample(self.audio, frame)
            fft = np.fft.rfft(sample*self.window)
            fft = np.abs(fft) / mx

            s = self.find_top_notes(fft,self.NOTES_DETECTED,self.threshold)
            self.all_notes += s
        return self.all_notes
    
    def create_note_dictionary(self):
        # loop 3: dictionary placement, mode value in C3-B4
        mode = 0
        self.mode_key = ''

        for row in self.all_notes:
            if row[2] > 0.2:
                try:
                    self.note_frames[row[1]] += 1
                except:
                    print(f"Error occured when placing: {row[1]}")

                if '3' in row[1] or '4' in row[1]:
                    if self.note_frames[row[1]] > mode:
                        self.mode_key = row[1]
                        mode = self.note_frames[row[1]]
            
            else:
                pass

        mu = self.keys.index(self.mode_key) - 4 # drop quarter octive, too biased for high frequencies
        std = 125
        def norm(int, mu, std): return np.e ** ((-(int - mu) ** 2) / std)

        # loop 4: normalization
        for k in self.note_frames.keys():
            ind = self.keys.index(k)
            self.note_frames[k] = int(norm(ind, mu, std) * self.note_frames[k])
        
        return self.note_frames

    def get_extreme_keys(self):
        low_key = None
        high_key = None

        for key in self.note_frames.keys():
            if not low_key and self.note_frames[key] > 0:
                ind = self.keys.index(key) + 4
                low_key = self.keys[ind]
            if self.note_frames[key] > 100:
                high_key = key

        return low_key, high_key
    
    def get_mode_key(self): return self.mode_key
    
def write_to_csv(data, headers = None):
    """
    Testing function to affirm functionality of class.
    """
    #TODO paramatize file_path
    file_path = 'C:\\Users\\Music\\BI\\Notes5.csv'
    
    with open(file_path, 'w', newline = '') as csv_file:
        writer = csv.writer(csv_file)
        if headers:
            writer.writerow(headers)

        for row in data:
            writer.writerow(row)

"""
Example usage:

VOCAL_WAV = "C:\\Users\\vocals.wav"
tracker = Track_Analysis(VOCAL_WAV)
ar = tracker.create_note_array()
nf = tracker.create_note_dictionary()
print(nf)
#write_to_csv(ar, ['Frequency','Note','Magnitude'])

VOCAL_WAV = "C:\\Users\\vocals2.wav"
tracker = Track_Analysis(VOCAL_WAV)
ar = tracker.create_note_array()
nf = tracker.create_note_dictionary()
print(nf)
"""


