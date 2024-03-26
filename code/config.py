# config.py 
# Note: ('Almost' the same as my youtube MP3 converter project's configuration file)

# Initialize linguistic processing variables
ROOT_ASSET_PATH = "\\assets\\" # adjust root path
LANGUAGE_CODE_MAP1 = "code_language_map.json"
LANGUAGE_CODE_MAP2 = "fasttext_language_map.json"
FASTTEXT_MODEL = 'lid.176.ftz'

# General use
CURRENT_TRACK_TITLE = ''
CURRENT_TRACK_ARTIST = '' # configurated in get_trackID (spotify_analysis.py)

# Spotify
CLIENT_ID = '' # Add id
CLIENT_SECRET = '' # Add secret

SPOTIFY_API_ENDPOINT = 'https://accounts.spotify.com/api/token'
SPOTIFY_TOKEN = '' # Valids for 30-60 mins every run
CURRENT_TRACK_FEATURES = ''

# Functions
def refresh_spotify_token():
    global SPOTIFY_TOKEN
    import base64
    import requests
    """
    Using client id and secret in config file, generates and sets access token string in config.py
    Access token is valid for 1 hour every generation.
    """
    client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    
    # Encode with base64
    encoded_credentials = base64.b64encode(client_credentials.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_credentials}'
    }
    payload = {
        'grant_type': 'client_credentials',
    }

    # Post request for access token
    response = requests.post(SPOTIFY_API_ENDPOINT, headers=headers, data=payload)

    if response.status_code == 200:
        SPOTIFY_TOKEN = response.json()['access_token']
        print(f"Spotify Access Token created.")
    else:
        print(f"Failed to obtain access token. Status code: {response.status_code}")
