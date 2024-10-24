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

# pygame mixer for playing mp3s
pygame.mixer.init()

# File to store the NFC to MP3 associations
nfc_mapping_file = "nfc_mp3_mapping.json"

# Function to load the tag-MP3 mappings
def load_nfc_mapping():
    try:
        with open(nfc_mapping_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

nfc_mapping = load_nfc_mapping()

# read tag
def read_nfc_tag():
    print("Waiting for an NFC card...")
    uid = pn532.read_passive_target(timeout=5.0)
    if uid is None:
        return None
    return ''.join([f'{i:02X}' for i in uid])

# play associated file when a tag is scanned
def play_mp3(tag_uid):
    if tag_uid in nfc_mapping:
        mp3_file = nfc_mapping[tag_uid]
        print(f"Playing {mp3_file}")
        pygame.mixer.music.load(mp3_file)
        pygame.mixer.music.play()
    else:
        print("No MP3 associated with this tag.")

# Main loop to listen for NFC tag scans
while True:
    tag_uid = read_nfc_tag()
    if tag_uid:
        play_mp3(tag_uid)
    else:
        print("No tag detected.")
