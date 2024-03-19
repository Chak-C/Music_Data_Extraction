# Music  Extraction

## Problem Statement

Given a list of tracks in MP3 formats, produce or extract a series of data relevant to the files and store them in CSV files (utf-8).

## Music PowerBI Dashboard Project Link

[https://github.com/Chak-C/PBI_playlist_dashboard]

## About the project

This project aims to break down a musical piece and retrieve relevant data (check below) through integrating multiple mathematical approaches, deep learning (DL) and artifical intelligence 
(AI) models together. Because the final solution is ran on 132 files, great emphasis was placed on efficiency to accuracy loss rather than solely focused on maximizing accuracy.

In this project, the data extracted from 132 MP3 files are:

- Track Metadata: Title, Artist, Contributing Artists, Year, Genre, Duration (ms)
- File Data: Size (bits), Bit rate, Created Date, Last Modified Date
- Musical Data: Musical Notation (Key, with major and minor distinction), Tempo/BPM, Lowest Note, Highest Note, Mode Note, Frequencies of Spectrogram (C2-G#5)
- Linguistics Data: Language of track
- Spotify Data: Official Spotify title, official Spotify artist name, track dynamics (Acusticness, Danceability, Energy, Instrumentalness, Liveliness, Speechiness, Valence)
- Web Data: Artists'/Vocal Artists' gender
- Error Data

This project required the following third-party libraries and models to be made operational (more on their usages below):

- **Librosa**: A Python package for music and audio analysis
- **mutagen**: A Python library for writing and read audio file metadata
- **Spleeter**: A DL-based library for audio source separation developed by Deezer.
- **Whisper**: A Python library for audio watermarking and fingerprinting.
- **Fasttext**: A library for efficient learning of word representations and text classification developed by Facebook AI Research.
- **Langdetect**: A language detection library for identifying the language of text documents.
- **Scipy**: A Python library for scientific computing and technical computing, used for analyzing the time-series data in a spectrogram in this project.
- **Py-torch**: An open-source ML framework developed by Facebook AI Research. It provides a flexible and efficient platform for building and training deep learning models, with support for both CPU and GPU acceleration.
- **Spotipy**: A lightweight Python library for the Spotify Web API. It provides ease of information retrival and analysis related to Spotify track, artist and other information.

## Steps

- Step 1 : Adjust paramters (track_folder, output_root, vocal_output, output_name, error_name) in main_run.py then run the file to begin local data extraction
- Step 2.1 : Adjust paramters (folder_path, output_root, output_name) in main_run2.py then run the file to begin API data extraction
- Step 2.2 : Follow the prompt to validate API retrieved information to receive a final validated CSV file.
- Step 3.1 (optional) : In the PBI playlist dashboard project, save the distinct artists as csv file
- Step 3.2 (optional) : Adjust paramters (file_path) in VocalsGender.py to begin web scraping data extraction

## Data Retrieval

### <u> Metadata and File Data </u>

Relevant data: Title, Artist, Contributing Artists, Year, Genre, Duration (ms), Size (bits), Bit rate, Created Date, Last Modified Date

These data are mainly retrieved using Mutagen:

1. **Reading Metadata**: Read and store metadata and property tags from audio files.

2. **Supported Formats**: Mutagen supports various audio file formats, including MP3, WAV, FLAC etc. Which uses a unified interface for working with metadata across different file formats.

3. **Integration with Other Libraries**: Mutagen was easily integrated with other Python libraries for audio processing and analysis.

### <u> Musical Data </u>

Relevant data: Musical Notation (Key, with major and minor distinction), Tempo/BPM, Lowest Note, Highest Note, Mode Note, Frequencies of Spectrogram (C2-G#5)

After the initial load of MP3 file with librosa, the follow modules were used to perform calculations for corresponding data:

### KeyFinder.py

An interface for predicting the musical key of an audio file 

#### Procedures

0. Apply disection of harmonic and percussive elements of a track, this is defaulted off as we already separated instrumental and vocal elements of the track (Optional)
1. Apply librosas' Chroma Energy Normalized Statistics (Chroma CENS) on the audio to compress the differences of loudness/energy in each bins.
2. Map each note in the chormograph into a dictionary of keys.
3. Create a profile for each musical notation and calculate the correlation between itself and the Krumhansl-Kessler key profiles.
4. The profile with highest correlation is saved as the musical notation of the input track file.

Read 'Example usage' in the module for usages of the class.

### TrackAnalysis.py

An interface for analyzing highest, lowest, mode notes and the music spectrogram.

#### Procedures

0. Predefine variables for analysis; FPS, FFT window second, minimum recorded frequency, maximum recorded frequency, noise frequency, notes recorded per frame.
1. Use scipy to load the vocal wav file.
2. Apply Hanning window function onto the track and record peaks of frequency within the frame (frequency to note graph).
3. Calculate the note of peaks using frequency to note functions (see: [https://newt.phys.unsw.edu.au/jw/notes.html])
4. Record the frame of keys in a dictionary
5. Repeat step throughout track and return the final dictionary of keys.

Read 'Example usage' in the module for usages of the class.

### <u> Linguistics Data </u>

Relevant data: Language of track

After separating vocals and instrumental parts of the track, parse it into a transcription and language detection model to retrieve the vocal language of the track.

### MusicLinguistics.py

An interface for predicting the included language of an audio file 

#### Procedures

0. Initiate whisper model on either CPU or GPU (requires torch cuda) interface
1. Transcribe the vocal wav file with the whisper model
2. Parse the transcription text into langdetect (depricated) or fasttext model to retrieve the predicted language
3. Check the correlation of the prediction (Optional: Limitation, the correlation is meaningless if the transcription is initially incorrect)
4. Return the predicted language

Read 'Sample usages' in the module for usages of the class.

### <u> Spotify Data </u>

Relevant data: Official Spotify title, official Spotify artist name, and track dynamics. 

Majority functions overlap the module in my MP3 Converter and Recommender project.

### spotify_analysis.py, main_run2.py, main_run2-2.py

Interfaces for connecting to the Spotify API and presenting terminal UI given a folder of MP3 files.

#### Procedures

0. Set up client secret and client name in the config file
1. Request for an authentication access token
2. Use it to authenticate and activate Spotipy
3. Retrieve searched title/artist and present it to the viewer in terminal for validation
4. If it is correct, save the information. Otherwise, prompt the user for a more specific search (or quit if track is not available in Spotify)
5. Retrieve track dynamics
6. Produce a final CSV file

Read 'Example usage' in the module for usages of the class.

### <u> Web Data </u>

Relevant data: Vocal Artist gender. 

Primarily using requests and BeautifulSoup, JSON responses are received and relevant data is scavaged accordingly.

### VocalsGender.py

An interface for crawling [https://musicbrainz.org] for vocal artist gender of each track given a CSV of artist names.

#### Procedures

0. Define input and output filepaths
1. Load the input file with CSV library
2. For each artist in the input, create a request to the web and retrieve a JSON output
3. Crawl the JSON output for the relevant data and record it in a list.
4. Repeat until the input file is exhausted.
5. Return the results in a CSV file.

Read 'Example usage' in the module for usages of the class.
