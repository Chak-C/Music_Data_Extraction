import os, csv, datetime
import librosa, tqdm
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from time import sleep

from TrackAnalysis import Track_Analysis
from ExtractVocals import Extract_Vocal
from KeyFinder import Key_Finder
from MusicLinguistics import Music_Linguistics

#TODO: retrieve gender information

# Please use valid and accessible folders before running code
TRACK_FOLDER = "C:\\Users\\Alvis\\Desktop\\Music"
OUTPUT_ROOT = "C:\\Users\\Alvis\\Desktop\\Music\\BI\\Extraction\\output\\"
VOCAL_OUTPUT = "C:\\Users\\Alvis\\Desktop\\Music\\BI\\Extraction\\output\\Separated\\"

OUTPUT_NAME = "data.csv"
ERROR_NAME = "errors.csv"
FILE_PATH = OUTPUT_ROOT + OUTPUT_NAME
ERROR_PATH = OUTPUT_ROOT + ERROR_NAME

HEADER = ["Title", "Artists", "Contributing Artists", "Year", "Genre", "Duration", "Size",  
"Bit rate", "Created Date", "Last Modified Date", "Key", "Tempo", "Language", "Lowest Note", 
"Highest Note", "Mode Note", "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", 
"A2", "A#2", "B2", "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", 
"A#3", "B3","C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", 
"B4", "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
"C6", "C#6", "D6", "D#6", "E6"]

ERROR_HEADER = ['FilePath','Error']

def extract_prim_data(file):
    primary_data = {}

    data = MP3(file, ID3=EasyID3)

    # Title
    primary_data['title'] = data.get('title', [None])[0]
    # Artist
    primary_data['artist'] = data.get('albumartist', [None])[0]
    # Contributing artists
    primary_data['contributing_artists'] = data.get('artist', [None])[0]
    # Year
    primary_data['year'] = data.get('date', [None])[0]
    # Genre
    primary_data['genre'] = data.get('genre', [None])[0]
    # Duration
    primary_data['duration'] = int(data.info.length)
    # File size
    primary_data['size'] = os.path.getsize(file)
    # Bit rate
    primary_data['bit_rate'] = data.info.bitrate

    # Created date
    cdate = os.path.getctime(file)
    cdate = datetime.datetime.fromtimestamp(int(cdate))
    cdate = cdate.strftime("%Y-%m-%d %H:%M:%S")
    primary_data['created_date'] = cdate

    # Last modified date
    mdate = os.path.getctime(file)
    mdate = datetime.datetime.fromtimestamp(int(mdate))
    mdate = mdate.strftime("%Y-%m-%d %H:%M:%S")
    primary_data['last_modified_date'] = mdate

    return primary_data

def write_to_csv(data, file_path, header, function = 'append'):
    """
    Function can be new_file or append, default to append
    """
    if function == 'append':
        mode = 'a' if os.path.exists(file_path) else 'w'

    elif function == 'new_file':
        mode = 'w'
        version = 2
        while os.path.exists(file_path):
            file_path = file_path + str(version)
            version += 1
    
    with open(file_path, mode, encoding='utf-8', newline = '') as csv_file:
            writer = csv.writer(csv_file)
            if header and mode == 'w':
                writer.writerow(header)

            for row in data:
                writer.writerow(row)

        

data = []
errors = []
c = 0

for root, dir, folder in os.walk(TRACK_FOLDER):
    for track in tqdm.tqdm(folder):
        if track.lower().endswith('.mp3'):
            
            #if track = '転生林檎 (Orchestra).mp3': # handle tracks that are instrumental separately (until next update)
            #    continue
            if root == 'C:\\Users\\Alvis\\Desktop\\Music\\AFTER_BI':
                continue

            file_path = os.path.join(root, track)

            if c%5 == 6:
                break
            
            try:
                # Basic metadata
                meta_data = extract_prim_data(file_path)
                meta_data = list(meta_data.values())

                # Extract vocals
                separator = Extract_Vocal(file_path, VOCAL_OUTPUT)
                separator.separate()
                vocals_folder, vocals_wav = separator.get_vocal_path()
                sleep(3)
                
                # Language detect
                translator = Music_Linguistics()
                translator.transcribe(vocals_wav)
                language = translator.detect_fasttext()

                # Predict musical key
                y, sr = librosa.load(vocals_wav, sr = None, mono = True) # must be vocals (unless instrumental), otherwise prediction is inaccurate
                key_finder = Key_Finder(y, sr)
                musical_key = key_finder.get_key()
                key_finder.print_key(f'[{track}] - ')

                # Get BPM/tempo of track
                y, sr = librosa.load(file_path, sr = None, mono = True)
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                sleep(3)

                # Note count
                tracker = Track_Analysis(vocals_wav)
                tracker.create_note_array()
                note_data = tracker.create_note_dictionary()
                note_data = list(note_data.values())
                low_key, high_key = tracker.get_extreme_keys()
                mode_key = tracker.get_mode_key()

                # List extend
                predicted_data = [musical_key, int(tempo), language, low_key, high_key, mode_key]
                meta_data.extend(predicted_data)
                meta_data.extend(note_data)

                data.append(meta_data)

                c += 1
                sleep(1)

            except Exception as e:
                errors.append([file_path, e])

            # Delete vocals file (if made)
            separator.delete_folder()
        else:
            continue
    continue

#write_to_csv(data=data,file_path=OUTPUT_ROOT+'corrected_keys',header=['title','key','tempo'])
write_to_csv(data=data,file_path=FILE_PATH,header=HEADER)
write_to_csv(data=errors,file_path=ERROR_PATH,header=ERROR_HEADER)

"""
def write_to_csv(data, output_name, dictionary):
    ""
    takes dictionary of data (dictionary = true)
    takes list of data (dictionary = false), saves/appends data to output_name
    ""
    headers = data[0].keys() if data else []
    with open(output_name, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
"""

