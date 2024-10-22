# NFC Raspberry Pi Media Player
Codebase for connecting a PN-532 NFC chip to a Raspberry Pi 4 to result in an on demand mp3 player and spotify playback controller

# SPI 
Conifrm that SPI is enabled on the Pi by `sudo raspi-config` -> interfacing options -> SPI 

SPI Python tools 
```
sudo apt update
sudo apt-get install python3-dev python3-pip
sudo pip3 install spidev
sudo pip3 install adafruit-circuitpython-pn532
```
