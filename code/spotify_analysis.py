import spotipy
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import time

import config as c

_sp = ''

def activate_spotify():
    """
    Activates spotipy.
    Params: repeated (boolean), always use as false, true is for recursion purposes only
    """
    global _sp

    if not c.SPOTIFY_TOKEN:
        print('Initiating Spotify access token.')
        c.refresh_spotify_token()
    
    _sp = spotipy.Spotify(auth=c.SPOTIFY_TOKEN)
    _sp.me

    return None

def handle_spotify_exception(func):
    def wrapper(*args, **kwargs):
        try:
            # Call decorated function
            return func(*args, **kwargs)
        except spotipy.SpotifyException:
            #Handle exception
            print('Refreshing Spotify access token')
            # Reset token
            c.refresh_spotify_token()
            # Reactive spotipy
            activate_spotify()
            time.sleep(1)
            return func(*args, **kwargs)
    return wrapper

@handle_spotify_exception
def get_trackID(track_name, artist = None):
    """
    Returns the Spotify ID of a track (Not case sensitive)
    Params: track_name, the name of the track (required)
            artist, the name of the artist (optional)
    """
    if artist:
        query = f"track:{track_name} artist:{artist}"
    else:
        query = f"track:{track_name}"
    
    results = _sp.search(q=query,type='track',limit=1)
    if results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        c.CURRENT_TRACK_TITLE = track_name
        c.CURRENT_TRACK_ARTIST = results['tracks']['items'][0]['artists'][0]['name']
        return track_id
    else:
        print('Track ID not found. It may not exist in the Spotify library. Please confirm track_name and artist are valid and retry.')
        return None

@handle_spotify_exception
def get_features(track_id):
    """
    Returns the statistic features of the track
    Params: track_id, the spotify ID of the track
    """
    track_features = _sp.audio_features(track_id)
    df = pd.DataFrame(track_features, index = [0])
    df_features = df.loc[:, ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
    return df_features

def feature_plot(features, figsize):
    """
    Creates a hexagonal rating graph for one feature set.
    Param: features (list containing 6 statistics ranging 0-1), figsize (int)
    Example: 
    fig = feature_plot(df_features, 18)
    plt.show()
    """
    labels = list(features)[:]
    stats = features.mean().tolist()

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint = False)

    stats = np.concatenate((stats, stats[0]))
    angles = np.concatenate((angles, [angles[0]]))

    fig = plt.figure(figsize=(figsize,figsize))

    ax = fig.add_subplot(221, polar = True)
    ax.plot(angles, stats, 'o-', linewidth = 2, label = 'Features', color = 'gray')
    ax.fill(angles, stats, alpha = 0.25, facecolor = 'gray')
    ax.set_thetagrids(angles[0:7]*180/np.pi, labels, fontsize = 13)

    ax.set_rlabel_position(250)
    plt.yticks([0.2, 0.4, 0.6, 0.8], ['0.2', '0.4', '0.6', '0.8'], color = 'gray', size = 12)
    plt.ylim(0,1)

    plt.legend(loc = 'best', bbox_to_anchor = (0.1, 0.1))

    return fig

def feature_plot2(feature1, feature2, figsize):
    labels = list(feature1)[:]
    stats = feature1.mean().tolist()
    stats2 = feature2.mean().tolist()

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint = False)

    stats = np.concatenate((stats, [stats[0]]))
    stats2 = np.concatenate((stats2, [stats2[0]]))
    angles = np.concatenate((angles, [angles[0]]))

    fig = plt.figure(figsize=(figsize,figsize))

    ax = fig.add_subplot(111, polar = True)
    ax.plot(angles, stats, 'o-', linewidth = 2, label = 'Features 1', color = 'gray')
    ax.fill(angles, stats, alpha = 0.25, facecolor = 'r')
    ax.set_thetagrids(angles[0:7] * 180/np.pi, labels, fontsize = 13)

    ax.set_rlabel_position(250)
    plt.yticks([0.2, 0.4, 0.6, 0.8], ['0.2','0.4','0.6','0.8'], color = 'gray', size = '12')
    plt.ylim(0, 1)

    ax.plot(angles, stats2, 'o-', linewidth = 2, label = 'Feature 2', color = 'm')
    ax.fill(angles, stats2, alpha = 0.25, facecolor = 'b')
    ax.set_title('Mean Values of the audio features')
    ax.grid(True)

    plt.legend(loc = 'best', bbox_to_anchor = (0.1, 0.1))

    plt.tight_layout()
    return fig

def get_track_recommendation(track_id, limit):
    """
    Gets X amount of recommendations for a track.
    Param: track_id, limit (int)
    Return: JSON response
    """
    limit = limit
    recUrl = f"https://api.spotify.com/v1/recommendations?limit={limit}&seed_tracks={track_id}"

    header = {
        "Authorization": "Bearer " + c.SPOTIFY_TOKEN
    }

    try:
        res = requests.get(url=recUrl, headers = header)
    except spotipy.SpotifyException:
        c.refresh_spotify_token()
        res = requests.get(url=recUrl, headers = header)
        
    return res.json()

@handle_spotify_exception
def get_recommendation_features(json_response):
    """
    Extract the analytical stats of each track in a json_response
    Param: json_response
    Return: Dataframe of features
    """
    feat_df = pd.DataFrame()

    for track in json_response['tracks']:
        audio_feat = _sp.audio_features(track['id'])
        local_feat = pd.DataFrame(audio_feat, index=[0])
        local_feat.insert(0, 'track_id', track['id'])
        feat_df = pd.concat([feat_df, local_feat], ignore_index=True)
        
    return feat_df

def feat_similarity(feature1, feature2, method):
    """
    Calculates similarity of both lists using pearson correlation coefficient or euclidean_norm
    Return: value between 0 to 1
    Param: feature1 (panda Dataframe, or a list), feature2 (Dataframe or list)
        method: 'pearson' or 'euclidean_norm'
    """
    if method.lower() == 'pearson':
        return np.corrcoef(np.array(feature1), np.array(feature2))[0, 1]
    if method.lower() == 'euclidean_norm':
        euclidean_distance = np.linalg.norm(np.array(feature1) - np.array(feature2))
        euclidean_distance = 1 / (1 + euclidean_distance)
        return euclidean_distance
    return None

def recommend_from_track(track_id, search_limit, method, threshold, show_limit):
    """
    Using track title and artist, create a list of recommendations with high similarity
    Note: If pearson, 0.9 threshold is recommended. If Euclidean_norm, 0.75 threshold is recommended
    Param:
        title (string), artist (optional string)
        search_limit: the number of tracks searched for comparison (int)
        method: the method used for comparison ('pearson','euclidean_norm')
        threshold: the required level of similarity
        show_limit: the number of recommendations showed
    Return:
        A pd.DataFrame containing the track titles, artists, duration, popularity and similarity (for UI).
        A pd.DataFrame containing the track features (for graphing).
    """
    # Get general recommendations
    recommendation_list = get_track_recommendation(track_id, search_limit)
    # Retrieve and save the current track feature
    track_feature = get_features(track_id)
    c.CURRENT_TRACK_FEATURES = track_feature

    # Retrieve features of recommended tracks
    recommendation_feats = get_recommendation_features(recommendation_list)
    recommendation_list = pd.DataFrame(recommendation_list['tracks'])
    
    # Initiate return DataFrames
    final_rec_feats, final_rec_similarity, final_recommendation_list = pd.DataFrame(), [], pd.DataFrame()
    
    # Similarity comparison
    for index in range(1, 20):
        rec = recommendation_feats.iloc[index]
        rec_features = rec[['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
        sim = feat_similarity(track_feature, rec_features.tolist(), method)
        if  sim > threshold:
            final_rec_feats = pd.concat([rec_features.to_frame().T, final_rec_feats], ignore_index=True)
            final_rec_similarity.append({sim})
            final_recommendation_list = pd.concat([recommendation_list.iloc[index].to_frame().T,final_recommendation_list], ignore_index=True)
        else:
            continue

    # Tidy data
    final_rec_similarity = pd.DataFrame(final_rec_similarity)
    final_rec_similarity.columns = ['similarity']

    final_recommendation_list = pd.concat([final_recommendation_list, final_rec_similarity], axis=1)
    final_recommendation_list = final_recommendation_list[['name', 'artists', 'preview_url', 'duration_ms', 'popularity', 'similarity']].iloc[:show_limit]
    
    return final_recommendation_list, final_rec_feats

def parse_miliseconds(ms):
    total_seconds = ms / 1000

    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)

    return f"{minutes}:{seconds:02d}"
