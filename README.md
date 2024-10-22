# NFC Raspberry Pi Media Player
Codebase for connecting a PN-532 NFC chip to a Raspberry Pi 4 to result in an on demand mp3 player and spotify playback controller

## Physical Connections
|**PN532 Pin** |	**Raspberry Pi Pin** |	**Description**|
|---------| ----------- | ---------- |
|SCK |	GPIO 11 (Pin 23)	| Serial Clock (SCK)|
|MSO	| GPIO 9 (Pin 21)	| Master In Slave Out (MISO) |
|MOSI	| GPIO 10 (Pin 19)	| Master Out Slave In (MOSI) |
|SS	| GPIO 8 (Pin 24)	| Chip Select (SS/CS) |
|VCC	| Pin 1 (3.3V)	| Power |
|GND	| Pin 6 (Ground)	| Ground |
|RSTO	| GPIO 25 (Pin 22) |	Reset |



## SPI 
Conifrm that SPI is enabled on the Pi by `sudo raspi-config` -> interfacing options -> SPI 

SPI Python tools 
```
sudo apt update
sudo apt-get install python3-dev python3-pip
sudo pip3 install spidev
sudo pip3 install adafruit-circuitpython-pn532
```
Create a file called spi_test.py with the same code as that of the file provided.
