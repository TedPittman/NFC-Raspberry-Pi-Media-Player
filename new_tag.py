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
nfc_mapping_file = "nfc_mp3_mapping.json"

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

# write to an NFC tag with path for an MP3 file
def associate_nfc_with_mp3(tag_uid, mp3_file):
    nfc_mapping[tag_uid] = mp3_file
    save_nfc_mapping(nfc_mapping)
    print(f"Tag {tag_uid} has been assigned to {mp3_file}")


# main loop to assign an MP3 to an NFC tag
mp3_file = "/home/pi/Desktop/nfcproject/Music/07 - Drive Back.mp3"  # Set this to the path of your MP3 file
print("Place the NFC tag to associate with the MP3 file.")
tag_uid = read_nfc_tag()

if tag_uid:
    associate_nfc_with_mp3(tag_uid, mp3_file)
else:
    print("No tag detected.")
