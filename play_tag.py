import busio
import digitalio
import board
from adafruit_pn532.spi import PN532_SPI
import time
import pygame
import json
import sys
import select
import threading
from collections import deque
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from spotify_control import play_spotify_track, control_spotify_playback, get_spotify_client

# configure SPI
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = digitalio.DigitalInOut(board.D8)  # chip select connected to SS/CS pin
reset_pin = digitalio.DigitalInOut(board.D25)  # reset connected to RSTO pin

pn532 = PN532_SPI(spi, cs_pin, reset=reset_pin)

# pygame mixer for playing mp3s
pygame.mixer.init()

# file to store the NFC to MP3 and Spotify track URI associations
nfc_mapping_file = "nfc_mapping.json"

# load Spotify client
sp = get_spotify_client()

# function to load the mappings
def load_nfc_mapping():
    try:
        with open(nfc_mapping_file, "r") as f:
            data = json.load(f)
            print("Successfully loaded NFC mapping file.")
            return data
    except FileNotFoundError:
        print(f"Error: File '{nfc_mapping_file}' not found.")
        return {}

nfc_mapping = load_nfc_mapping()

# prompt user to choose whether mp3 or spotify will be played from a tag
def prompt_user_for_playback_method():
    while True:
        user_choice = input("Scan detected. Choose playback method:\n1: MP3\n2: Spotify\nChoice: ")
        if user_choice == '1':
            return 'mp3'
        elif user_choice == '2':
            return 'spotify'
        else:
            print("Invalid choice. Please select 1 or 2.")

playback_method = prompt_user_for_playback_method()

print("Waiting for an NFC card...")
'''
read_passive_target(card_baud: int = micropython.const, timeout: float = 1) -> bytearray | None
Wait for a MiFare card to be available and return its UID when found.
Will wait up to timeout seconds and return None if no card is found, 
otherwise a bytearray with the UID of the found card is returned.
'''
def read_nfc_tag():
    uid = pn532.read_passive_target(timeout=5.0)
    if uid is None:
        return None
    return ''.join([f'{i:02X}' for i in uid])

# play MP3 file associated with NFC tag
def play_mp3(tag_uid):
    if tag_uid in nfc_mapping:
        tag_data = nfc_mapping[tag_uid]
        if "mp3" in tag_data:
            mp3_file = tag_data["mp3"]
            print(f"Playing {mp3_file}")
            
            # load mp3 metadata
            try:
                metadata = MP3(mp3_file, ID3=EasyID3)
                title = metadata.get('title', ['Unknown Title'])[0]
                artist = metadata.get('artist', ['Unknown Artist'])[0]
                album = metadata.get('album', ['Unknown Album'])[0]
                track_info = f"{title} by {artist} from the album {album}."
                print(track_info)
            except Exception as e:
                print(f"Failed to load metadata for {mp3_file}: {e}")

            # play file
            try:
                pygame.mixer.music.load(mp3_file)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Error playing MP3 file {mp3_file}: {e}")
        else:
            print("No MP3 associated with this tag.")
    else:
        print("Scanned tag not found in NFC mapping.")

# play Spotify track associated with tag
def play_spotify_from_tag(tag_uid):
    if tag_uid in nfc_mapping:
        tag_data = nfc_mapping[tag_uid]
        if "spotify" in tag_data:
            track_uri = tag_data["spotify"]
            play_spotify_track(track_uri)
            print(f"Playing Spotify track associated with UID {tag_uid}")
        else:
            print("No Spotify track associated with this tag.")
    else:
        print("Tag not found in NFC mapping file.")

is_paused = False

# keyboard input handling function
def keyboard_input_loop():
    global is_paused

    print("Controls: [p] Pause/Play, [s] Stop, [+] Volume Up, [-] Volume Down")
    
    # spotify client once at the start
    sp = get_spotify_client()

    valid_keys = {'p', 's', '+', '-'}

    while True:
        # non blocking check for input
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            # read full input line
            user_input = sys.stdin.readline().strip().lower()
            
            # validate the entire line at once
            if len(user_input) == 1 and user_input in valid_keys:
                # is a valid key
                try:
                    if playback_method == 'spotify':
                        playback = sp.current_playback()
                        if user_input == 'p':  # pause or unpause playback
                            if playback and playback.get('is_playing'):
                                control_spotify_playback('pause')
                            else:
                                control_spotify_playback('resume')
                        elif user_input == 's':  # stop playback
                            control_spotify_playback('stop')
                        elif user_input == '+':  # increase volume
                            control_spotify_playback('volume_up')
                        elif user_input == '-':  # decrease volume
                            control_spotify_playback('volume_down')
                    elif playback_method == 'mp3':
                        # MP3 controls
                        if user_input == 'p':  # pause or unpause playback
                            if pygame.mixer.music.get_busy():
                                if is_paused:
                                    pygame.mixer.music.unpause()
                                    print("MP3 resumed.")
                                    is_paused = False
                                else:
                                    pygame.mixer.music.pause()
                                    print("MP3 paused.")
                                    is_paused = True
                        elif user_input == 's':  # stop playback
                            pygame.mixer.music.stop()
                            print("MP3 playback stopped.")
                            is_paused = False
                        elif user_input == '+':  # increase volume
                            current_volume = pygame.mixer.music.get_volume()
                            pygame.mixer.music.set_volume(min(1.0, current_volume + 0.1))
                            print(f"MP3 volume increased to {pygame.mixer.music.get_volume():.1f}")
                        elif user_input == '-':  # decrease volume
                            current_volume = pygame.mixer.music.get_volume()
                            pygame.mixer.music.set_volume(max(0.0, current_volume - 0.1))
                            print(f"MP3 volume decreased to {pygame.mixer.music.get_volume():.1f}")
                    else:
                        print(f"Invalid input: {user_input}. Please use the correct control keys.")

                except Exception as e:
                    print(f"Error handling keyboard input: {e}")
                    try:
                        sp = get_spotify_client()
                    except Exception as reconnect_error:
                        print(f"Failed to reconnect: {reconnect_error}")
            else:
                # input line is not one of valid keys
                print(f"Invalid input: '{user_input}'. Please use one of the given controls: (p, s, -, +)")
        
        time.sleep(0.1)

is_paused = False

# NFC scanning function
def nfc_scan_loop():
    cooldown_time = 2.0
    last_scan_time = 0
    global is_paused

    while True:
        current_time = time.time()
        
        # check tag if cooldown period passed
        if current_time - last_scan_time >= cooldown_time:
            tag_uid = read_nfc_tag()
            if tag_uid:
                print(f"Scanned UID: {tag_uid}")  # debug to find UID
                if playback_method == 'mp3':
                    play_mp3(tag_uid)
                elif playback_method == 'spotify':
                    play_spotify_from_tag(tag_uid)
                last_scan_time = time.time()  # reset cooldown
                is_paused = False

# start both NFC scanning and keyboard input handling in parallel
nfc_thread = threading.Thread(target=nfc_scan_loop)
keyboard_thread = threading.Thread(target=keyboard_input_loop)

nfc_thread.start()
keyboard_thread.start()

# wait for both threads to finish, which they won't unless interrupted
nfc_thread.join()
keyboard_thread.join()
