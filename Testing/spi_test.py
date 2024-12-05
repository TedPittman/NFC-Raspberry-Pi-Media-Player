import board
import busio
import digitalio
from adafruit_pn532.spi import PN532_SPI

# configure SPI
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = digitalio.DigitalInOut(board.D8)  # chip select connected to SS/CS pin
reset_pin = digitalio.DigitalInOut(board.D25)  # reset connected to RSTO pin

pn532 = PN532_SPI(spi, cs_pin, reset=reset_pin)

# check firmware version and connection
ic, ver, rev, support = pn532.firmware_version
print(f"Found PN532 with firmware version: {ver}.{rev}")

# read cards
pn532.SAM_configuration()

print("Waiting for an NFC card...")
while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is None:
        continue
    print(f"Found card with UID: {uid}")
