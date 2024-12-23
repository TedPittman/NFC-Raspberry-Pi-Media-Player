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
from mutagen.mp3 import MP3 
from mutagen.easyid3 import EasyID3
from spotify_control import play_spotify_track, control_spotify_playback

# configure SPI
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = digitalio.DigitalInOut(board.D8)  # chip select connected to SS/CS pin
reset_pin = digitalio.DigitalInOut(board.D25)  # reset connected to RSTO pin

pn532 = PN532_SPI(spi, cs_pin, reset=reset_pin)

# pygame mixer for playing mp3s
pygame.mixer.init()

# File to store the NFC to MP3 associations
nfc_mapping_file = "nfc_mapping.json"

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

# play associated file when a tag is scanned
def play_mp3(tag_uid):
    if tag_uid in nfc_mapping:
        # nested dictionary for tag UID
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

# check for keyboard input without blocking
def get_keyboard_input():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None

# NFC scanning function
def nfc_scan_loop():
    cooldown_time = 1.0
    last_scan_time = 0
    global is_paused

    while True:
        current_time = time.time()
        
        # check tag if cooldown period passed
        if current_time - last_scan_time >= cooldown_time:
            tag_uid = read_nfc_tag()
            if tag_uid:
                # print(f"Scanned UID: {tag_uid}")  # debug to find UID
                play_mp3(tag_uid)
                last_scan_time = current_time  # reset cooldown
                is_paused = False
            # time.sleep(0.1)

# keyboard input handling function
def keyboard_input_loop():
    global is_paused
    
    print("Controls: [p] Pause/Play, [s] Stop, [+] Volume Up, [-] Volume Down")

    while True:
        user_input = get_keyboard_input()
        if user_input:
            if user_input == 'p':  # pause or unpause playback
                if pygame.mixer.music.get_busy():  # if music is playing
                    if is_paused:
                        pygame.mixer.music.unpause()
                        print("Playback resumed.")
                        is_paused = False
                    else:
                        pygame.mixer.music.pause()
                        print("Playback paused.")
                        is_paused = True
                else:
                    print("No track is playing to pause or resume.")
            elif user_input == 's':  # stop playback
                pygame.mixer.music.stop()
                is_paused = False
                print("Playback stopped.")
            elif user_input == '+':  # increase volume
                current_volume = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(min(1.0, current_volume + 0.1))
                print(f"Volume increased to {pygame.mixer.music.get_volume():.1f}")
            elif user_input == '-':  # decrease volume
                current_volume = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(max(0.0, current_volume - 0.1))
                print(f"Volume decreased to {pygame.mixer.music.get_volume():.1f}")
        time.sleep(0.1)

is_paused = False

# start both NFC scanning and keyboard input handling in parallel
nfc_thread = threading.Thread(target=nfc_scan_loop)
keyboard_thread = threading.Thread(target=keyboard_input_loop)

nfc_thread.start()
keyboard_thread.start()

# wait for both threads to finish, which they won't unless interrupted
nfc_thread.join()
keyboard_thread.join()
