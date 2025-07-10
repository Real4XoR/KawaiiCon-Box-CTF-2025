# KawaiiCon-Box-CTF-2025

# Challenge 1 - Padlock Riddle

First box contains multiple locks on a rod with loads on keys that could open any one of them. Riddle to find four keys with numbers on them to unlock combo lock.

### Materials Required:

- 10-15 combo padlocks
- 30 keys

# Challnge 2 - Smart Camera

Have a local web server run on ESP32 and a blacked out box adjacent to the main box. Main box only has a piece of paper with a wireless network to connect, credentials for the wireless network, and a URL where the webapp is hosted locally. Vulnerable login portal (SQLI), gets redirected to dashboard with loads of local IP addresses. One of them leads to the actuial camera in the box. Camera is looking at QR code that contains information on how to get code for the combo lock.

### Materials Required:

- ESP32 enabled board (Arduino Nano ESP32)
- IP camera (with night vison)
- Wood
- Black paint
- Combo padlock

# Challenge 3 - NFC Cracking

Setup a vulnerable NFC reader with a crap password or magic code. Let users try and crack it or read it off an existing card.

### Materials Required:

- NFC reader
- Programmable 125kHz RFID card
- Bad password or UID
- Servo

# Prizes

???

# Credits

This is a continuation of Dunderhay's box project from 2019: https://github.com/dunderhay/Kawaiicon-Box-CTF-2019
