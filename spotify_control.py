import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import time

# Spotify API credentials
SPOTIFY_CLIENT_ID = '61c50c52eef44c7ea1f2db70606fcf2c'
SPOTIFY_CLIENT_SECRET = '5cd9b77c241b4287b2bdf58b0650122e'
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-modify-playback-state user-read-playback-state'

# initialize Spotipy client with OAuth
sp = spotipy.Spotify(auth_manager = SpotifyOAuth(
    client_id = SPOTIFY_CLIENT_ID,
    client_secret = SPOTIFY_CLIENT_SECRET,
    redirect_uri = SPOTIFY_REDIRECT_URI,
    scope = SCOPE
))

# play a specific Spotify track
def play_spotify_track(track_uri):
    try:
        sp.start_playback(uris = [track_uri])
        print(f"Playing Spotify track: {track_uri}")
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error playing Spotify track: {e}")

# control playback
def control_spotify_playback(action):
    try:
        if action == 'pause':
            sp.pause_playback()
            print("Spotify playback paused.")
        elif action == 'resume':
            sp.start_playback()
            print("Spotify playback resumed.")
        elif action == 'stop':
            sp.pause_playback()
            print("Spotify playback stopped.")
        elif action == 'volume_up':
            current_volume = sp.current_playback()['device']['volume_percent']
            sp.volume(min(100, current_volume + 10))
            print("Spotify volume increased.")
        elif action == 'volume_down':
            current_volume = sp.current_playback()['device']['volume_percent']
            sp.volume(max(0, current_volume - 10))
            print("Spotify volume decreased.")
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error controlling Spotify playback: {e}")
