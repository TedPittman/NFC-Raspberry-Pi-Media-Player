import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Spotify API credentials
SPOTIFY_CLIENT_ID = '61c50c52eef44c7ea1f2db70606fcf2c'
SPOTIFY_CLIENT_SECRET = '5cd9b77c241b4287b2bdf58b0650122e'
SPOTIFY_REDIRECT_URI = 'http://localhost:9090'
SCOPE = 'user-modify-playback-state user-read-playback-state'

# Set the path for the .cache file
cache_path = os.path.expanduser('~/.spotify_cache')

# initialize Spotipy client with OAuth
_spotify_client = None
sp = None

def get_spotify_client():
    global _spotify_client, sp
    try:
        if _spotify_client is None:
            auth_manager = SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=SCOPE,
                open_browser=False,
                cache_path=cache_path
            )
            
            # Check if we already have a cached token
            if not os.path.exists(cache_path):
                print("\nFirst-time setup: You'll need to authenticate with Spotify.")
                print("1. Open this URL in a browser:")
                auth_url = auth_manager.get_authorize_url()
                print(f"\n{auth_url}\n")
                print("2. After authorizing, you'll be redirected to a non-working localhost URL.")
                print("3. Copy the ENTIRE URL from your browser's address bar, even if the page doesn't load.\n This starts with http://localhost:9090/?code=...")
                response_url = input("\nPaste the ENTIRE redirect URL here: ").strip()
                
                try:
                    code = auth_manager.parse_response_code(response_url)
                    token_info = auth_manager.get_access_token(code, as_dict=False)
                    print("\nAuthentication successful! You won't need to do this again.\n")
                except Exception as e:
                    print(f"\nError parsing response: {e}")
                    print("Please make sure you copied the entire URL from your browser.\n")
                    raise
            
            _spotify_client = spotipy.Spotify(auth_manager=auth_manager)
            sp = _spotify_client
        return _spotify_client
    except Exception as e:
        print(f"Error initializing Spotify client: {e}")
        raise

# Before using any spotify functions, add:
sp = get_spotify_client()

# play a specific Spotify track
def play_spotify_track(track_uri):
    try:
        sp.start_playback(uris=[track_uri])
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
    except Exception as e:
        print(f"Unexpected error: {e}")
