"""
I forgot that get_features was scripted so it returns a pandas dataframe with headers also.
If the fix in main_run2.py did not solve the issue (max token capacity), please run this script since the spotyify artist and name are recorded.

Note: some tracks cannot be searched even when they appear in the Spotify library (likely to be a language and query restriction), I manually found the 
    track id of the tracks on Spotify and ran get_features for them.

This error occured 5 / 133 tracks for me. Could not decipher why it is happening, much apologies.

Alternative fix:

import spotify_analysis as sa

sa.activate_spotify()
# load the track ID manually
asasda = sa.get_features('21st68V0VJNuUZDNFXkMrO')

print(asasda.iloc[0].tolist())
"""
import csv
import tqdm
import spotify_analysis as sa

INTPUT_NAME = 'feature_data.csv'
OUTPUT_NAME = 'feature_data2.csv'
ROOT_PATH = 'C:\\Users\\Alvis\\Desktop\\Music\\BI\\Extraction\\Output\\'
HEADER = ['title', 'spotify title', 'spotify artist', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']


def write_to_csv(data, file_path, header):    
    with open(file_path, 'w', encoding='utf-8', newline = '') as csv_file:
        writer = csv.writer(csv_file)
        if header:
            writer.writerow(header)

        for row in data:
            writer.writerow(row)

file = open(ROOT_PATH + INTPUT_NAME, 'r', encoding='utf-8')
data = csv.reader(file)

sa.activate_spotify()

new_data = []
count = 0
for row in tqdm.tqdm(data):
    if row[0] == 'title':
        continue

    new_row = [row[0],row[1],row[2]]
    tid = sa.get_trackID(row[1],row[2])
    if tid:
        feat = sa.get_features(tid)
        labels = feat.iloc[0].values.tolist()
        count += 1
    else:
        print(row[0])
        labels = ['','','','','','','']
    
    new_row.extend(labels)
    new_data.append(new_row)
write_to_csv(new_data,ROOT_PATH + OUTPUT_NAME,HEADER)
id = sa.get_trackID(row[1],row[2])
    