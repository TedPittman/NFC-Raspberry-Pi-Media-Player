import busio
import digitalio
import board
from adafruit_pn532.spi import PN532_SPI
import pygame
import json

# configure SPI
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = digitalio.DigitalInOut(board.D8)  # chip select connected to SS/CS pin
reset_pin = digitalio.DigitalInOut(board.D25)  # reset connected to RSTO pin

pn532 = PN532_SPI(spi, cs_pin, reset=reset_pin)

# pygame mixer for playing mp3 files
pygame.mixer.init()

# file to store the NFC to MP3 associations
nfc_mapping_file = "nfc_mapping.json"

# load the tag-MP3 mappings
def load_nfc_mapping():
    try:
        with open(nfc_mapping_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# save the tag-MP3 mappings
def save_nfc_mapping(mapping):
    with open(nfc_mapping_file, "w") as f:
        json.dump(mapping, f)

# Load existing mappings
nfc_mapping = load_nfc_mapping()

# Read the NFC tag
def read_nfc_tag():
    print("Waiting for an NFC card...")
    uid = pn532.read_passive_target(timeout=5.0)
    if uid is None:
        return None
    return ''.join([f'{i:02X}' for i in uid])

# write to an NFC tag with path for an MP3 file and URL
def associate_nfc_with_content(tag_uid, mp3_file = None, spotify_url = None):
    if tag_uid in nfc_mapping:
        print(f"Tag {tag_uid} is already assigned to {nfc_mapping[tag_uid]}, remapping...")
        # update dictionary
        if mp3_file:
            nfc_mapping[tag_uid]["mp3"] = mp3_file
        if spotify_url:
            nfc_mapping[tag_uid]["spotify"] = spotify_url
    else:
        print(f"Assigning new tag {tag_uid}")
        # initialize tag's mapping entry as empty dictionary if it doesn't exist
        nfc_mapping[tag_uid] = {}

        # update dictionary
        if mp3_file:
            nfc_mapping[tag_uid]["mp3"] = mp3_file
        if spotify_url:
            nfc_mapping[tag_uid]["spotify"] = spotify_url
        
    save_nfc_mapping(nfc_mapping)
    print(f"Tag {tag_uid} has been updated with MP3: {mp3_file} and Spotify: {spotify_url}")


# main loop to assign an MP3 or URL to an NFC tag
print("Would you like to associate an MP3 or a URL with an NFC tag?")
content_type = input("Enter 'mp3' for an MP3 file, 'url' for a Spotify URL, or 'both' for both: ").strip().lower()

# get MP3 and/or URL from the user
if content_type == "mp3" or content_type == "both":
    mp3_file = input("Enter the full path to the MP3 file: ").strip()

if content_type == "url" or content_type == "both":
    spotify_url = input("Enter the Spotify URL (e.g., spotify:track:abc123): ").strip()

print("Place the NFC tag to associate with the MP3 file and/or Spotify URL.")
tag_uid = read_nfc_tag()

if tag_uid:
    if content_type == "mp3":
        associate_nfc_with_content(tag_uid, mp3_file = mp3_file)
    elif content_type == "url":
        associate_nfc_with_content(tag_uid, spotify_url = spotify_url)
    elif content_type == "both":
        associate_nfc_with_content(tag_uid, mp3_file = mp3_file, spotify_url = spotify_url)
else:
    print("No tag detected.")