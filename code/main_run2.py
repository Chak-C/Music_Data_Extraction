"""
On execute, retrieves spotify feature data of all MP3 files within the FOLDER_PATH using the
title and artist shown on the properties page. Then saves the information in a CSV file.
"""

import os, csv
import tqdm
import spotify_analysis as sa
import config as c
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from termcolor import colored
import regex_spm

FOLDER_PATH = "C:\\Users\\Alvis\\Desktop\\Music"
OUTPUT_ROOT = "C:\\Users\\Alvis\\Desktop\\Music\\BI\\Extraction\\output\\"
OUTPUT_NAME = "feature_data.csv"
FILE_PATH = OUTPUT_ROOT + OUTPUT_NAME

HEADER = ['title', 'spotigy title', 'spotify artist', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']

def get_title_artist(file):
    data = MP3(file, ID3=EasyID3)

    return data.get('title', [None])[0], data.get('albumartist',[None])[0]

def write_to_csv(data, file_path, header):    
    with open(file_path, 'w', encoding='utf-8', newline = '') as csv_file:
        writer = csv.writer(csv_file)
        if header:
            writer.writerow(header)

        for row in data:
            writer.writerow(row)

sa.activate_spotify()

artists = {}
data = []

for root, dir, folder in os.walk(FOLDER_PATH):
    for track in tqdm.tqdm(folder):
        if track.lower().endswith('.mp3'):
            track_features = ['','','','','','','','']
            file_path = os.path.join(root, track)

            title, artist = get_title_artist(file_path)

            track_data = [title]

            if artist or artist in artists.keys():
                track_id = sa.get_trackID(title, artist)
            elif title:
                track_id = sa.get_trackID(title)
            else:
                track_data.extend(['','']) # no spotify title/artist
                track_data.extend(track_features)
                data.append(track_data)
                continue
            
            if not track_id or not artist or not artist in artists.keys():
                if not track_id: print(colored('NO TRACK DETECTED', 'red'))
                else: print(colored(f'VERIFYING NEW ARTIST: {artist}', 'green'))

                print(colored(f"[{title}] Recorded artist: {artist} New artist: {c.CURRENT_TRACK_ARTIST}", 'yellow'))

                print("\nChange the spotify artist name if incorrect <artist> (One repeat only)")
                print("If unsure, enter complete information in format <title, artist>")
                print("Press enter (or singular character) will confirm the presented data.\n")
                
                info = input(f"Your response: ")

                match regex_spm.fullmatch_in(info):
                    case r'^[^,]*,[^,]*$':
                        repeat = 're'
                        confirm_title, confirm_artist = str(info).split(',')
                        
                        # Repeat the process if user wants to continue searching
                        while repeat == 're':
                            track_id = sa.get_trackID(confirm_title.strip(), confirm_artist.strip())
                            print(colored(f"\n[{confirm_title}] Input artist: {confirm_artist}, Found artist: {c.CURRENT_TRACK_ARTIST}", 'yellow'))
                            repeat = input(f"Validate information, <title, artist> to try again, or anything (except ',') to leave loop:")

                            match  regex_spm.fullmatch_in(repeat):
                                case r'^[^,]*,[^,]*$':
                                    confirm_title, confirm_artist = str(repeat).split(',')
                                    repeat = 're'
                                case _:
                                    repeat = 'retreat'

                        pass
                    case r"^[0-9a-zA-Z][0-9a-zA-Z]*$":
                        confirm_artist = str(info)
                        track_id = sa.get_trackID(title.strip(), confirm_artist.strip())
                        print(colored(f"\n[{title}] Input artist: {confirm_artist}, Found artist: {c.CURRENT_TRACK_ARTIST}", 'yellow'))
                        pass
                    case _: # Information is correct, pass the match case
                        pass
                
            # If no track id, forfid
            if not track_id:
                track_data.extend(['',''])
                track_data.extend(track_features)
                data.append(track_data)
                print('moving on')
                continue
                    
            # if if-statement(s) does not proc, then track id must be correct
            artists[artist] = c.CURRENT_TRACK_ARTIST
            track_features = sa.get_features(track_id)
            track_features = track_features.iloc[0].values.tolist()
            print(f'[{title}] feature recorded')
            track_data.extend([c.CURRENT_TRACK_TITLE,c.CURRENT_TRACK_ARTIST])
            track_data.extend(track_features)
            data.append(track_data)
            c.CURRENT_TRACK_ARTIST = None
            continue

write_to_csv(data=data,file_path=FILE_PATH,header=HEADER)