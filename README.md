# NFC Raspberry Pi Media Player
This project enables a Raspberry Pi 4 to interact with an NFC reader (PN-532) for on-demand MP3 playback and Spotify control. NFC cards are configured to store references to either MP3 files or Spotify URIs, allowing users to scan cards and instantly trigger playback through local speakers.

Video Demo:
https://1drv.ms/v/c/c494ba4c4c4a6fff/EeMUgNFUigdGqCFDSd7KGJoBNKYO3_XPt4SFgwPU7al1_A?e=wuvliE

## Features
* NFC to MP3/Spotify Mapping: Each NFC card can store both an MP3 file path and a Spotify track URI, enabling dual functionality on a single card.
* Local MP3 Playback: Uses pygame for MP3 playback with support for pause/resume, stop, and volume control.
* Spotify Control: Allows playback of Spotify tracks mapped to NFC cards, using the Spotify API.
* Asynchronous Operation: Ensures NFC scanning and playback work seamlessly for both MP3 and Spotify tracks without interference.

## Physical Connections
Use GPIO pins to connect the chip to the Pi via SPI.
Here are the connections used for this project:
| **PN532 Pin** |	**Raspberry Pi Pin** | **Description** |
| --------- | ----------- | ---------- |
|SCK |	GPIO 11 (Pin 23) | Serial Clock (SCK)|
|MSO | GPIO 9 (Pin 21) | Master In Slave Out (MISO) |
|MOSI	| GPIO 10 (Pin 19) | Master Out Slave In (MOSI) |
|SS	| GPIO 8 (Pin 24)	| Chip Select (SS/CS) |
|VCC	| Pin 1 (3.3V)	| Power |
|GND	| Pin 6 (Ground)	| Ground |
|RSTO	| GPIO 25 (Pin 22) |	Reset |

## Miscellaneous
Assorted necessary python packages
```
sudo apt update
sudo apt-get install python3-dev python3-pip
sudo pip install mutagen
sudo pip install pygame
sudo pip install spotipy
```



## SPI 
Conifrm that SPI is enabled on the Pi by
`sudo raspi-config` -> interfacing options -> SPI 

You must physically switch the mode to SPI by removing the yellow plastic cover from the black housing with 2 yellow switches towards the edge of the chip.

Switch 1 is off switch 2 is on for SPI mode.

SPI Python tools 
```
sudo apt update
sudo apt-get install python3-dev python3-pip
sudo pip3 install spidev
sudo pip3 install adafruit-circuitpython-pn532
```
Create a file called [spi_test.py](spi_test.py) with the same code as that of the file provided for testing the connection to your Pi.

## NFC Tag UID Mapping
Each NFC card stores its unique UID in a JSON file (nfc_mapping.json). This file maps each tag’s UID to an MP3 file path and/or Spotify URI, allowing flexible content association:

MP3: Local file path for MP3 playback.
Spotify: Spotify track URI for streaming playback.
Example Mapping Structure:
json
```
{
  "AF6ACC1C": {
    "mp3": "/home/pi/Music/song.mp3",
    "spotify": "spotify:track:7Jsli31ZTv3TI28qcXzEkE"
  }
}
```
## Associating Content with Tags
Run [new_tag.py](new_tag.py) to add or update content mappings for NFC cards:
Select mp3, url, or both to define the type of content.
Scan the NFC card to store the content in nfc_mapping.json.


## Play mp3
run the provided [play_tag_mp3.py](play_tag_mp3.py) file.
This has included instructions for additional playback controls once a file starts playing, including pause/resume, stop, and volume control.


## Spotify Control
To get a URI from a given track, click three dots next to track, hit share, hold Alt key, select copy URI
run the provided [play_tag_spotify.py](play_tag_spotify.py) file.
This has included instructions for additional playback controls once a file starts playing, including pause/resume, stop, and volume control.



example URI: 
spotify:track:7FWFrfaypHHHxMyXR5eR6S


## Documentation
Adafruit pn532.spi commands
https://docs.circuitpython.org/projects/pn532/en/latest/api.html 

Spotify Developer notes
https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids
