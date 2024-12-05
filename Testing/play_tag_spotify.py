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
from spotify_control import play_spotify_track, control_spotify_playback, get_spotify_client

# configure SPI
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = digitalio.DigitalInOut(board.D8)  # chip select connected to SS/CS pin
reset_pin = digitalio.DigitalInOut(board.D25)  # reset connected to RSTO pin

pn532 = PN532_SPI(spi, cs_pin, reset=reset_pin)

# pygame mixer for playing mp3s
pygame.mixer.init()

# File to store the NFC to Spotify track URI associations
nfc_mapping_file = "nfc_mapping.json"

# load Spotify client
sp = get_spotify_client()

# Function to load the tag-MP3 mappings
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
# DISPLAY NFC DICTIONARY DATA
# print(f"Loaded NFC mapping: {nfc_mapping}")
# print(json.dumps(nfc_mapping, indent=4))


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

# function to play Spotify track associated with NFC tag
def play_spotify_from_tag(tag_uid):
    if tag_uid in nfc_mapping:
        # nested dictionary
        tag_data = nfc_mapping[tag_uid]

        if "spotify" in tag_data:
            track_uri = tag_data["spotify"]
            play_spotify_track(track_uri)
            print(f"Playing Spotify track associated with UID {tag_uid}")
        else:
            print("No Spotify track associated with this tag.")
    else:
        print("Tag not found in NFC mapping file.")

# check for keyboard input without blocking
def get_keyboard_input():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None

# keyboard input handling function
def keyboard_input_loop():
    print("Controls: [p] Pause/Play, [s] Stop, [+] Volume Up, [-] Volume Down")
    
    # Get spotify client once at the start
    sp = get_spotify_client()

    while True:
        user_input = get_keyboard_input()
        if user_input:
            try:
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
            except Exception as e:
                print(f"Error handling keyboard input: {e}")
                # If we get a connection error, try to reconnect
                try:
                    sp = get_spotify_client()
                except Exception as reconnect_error:
                    print(f"Failed to reconnect: {reconnect_error}")
        time.sleep(0.1)

# NFC scanning function
def nfc_scan_loop():
    cooldown_time = 5
    last_scan_time = 0
    # Get spotify client once at the start
    sp = get_spotify_client()

    while True:
        try:
            current_time = time.time()
            
            # check tag if cooldown period passed
            if current_time - last_scan_time >= cooldown_time:
                tag_uid = read_nfc_tag()
                if tag_uid:
                    print(f"Scanned UID: {tag_uid}")  # debug to find UID
                    play_spotify_from_tag(tag_uid)
                    last_scan_time = current_time  # reset cooldown
        except Exception as e:
            print(f"Error during NFC scanning: {e}")
            # If we get a connection error, try to reconnect
            try:
                sp = get_spotify_client()
            except Exception as reconnect_error:
                print(f"Failed to reconnect: {reconnect_error}")
        time.sleep(0.1)

# start both NFC scanning and keyboard input handling in parallel
nfc_thread = threading.Thread(target=nfc_scan_loop)
keyboard_thread = threading.Thread(target=keyboard_input_loop)

nfc_thread.start()
keyboard_thread.start()

# wait for both threads to finish, which they won't unless interrupted
nfc_thread.join()
keyboard_thread.join()
