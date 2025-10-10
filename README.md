# KawaiiCon-Box-CTF-2025

# Overview

A challenge box for KawaiiCon 2025. Solve the challenges, get a prize.

Overall cost: $250

## Challenge 1 - Padlock Riddle

There are two ways to open the box - either you solve the puzzle and get the combo lock code, or you pick the other lock. Both open the first box. 

#### Puzzle

eight locks with 35 keys

locks attached to chain 

only three keys work

all locks have letters on them 

all keys have ROT-X letters on them

letter correspond with the number of its place in alphabet e.g. A=1 B=2 ... Z=26

correct 3 digits will unlock combo pad lock

## Challnge 2 - Web Application

Have a local web server hosted on a Pi 4. Vulnerable login portal (SQLI), gets redirected to dashboard with loads of local IP addresses. Web application has three tabs; dashboard, cameras, and system. Users don't have permission to view the system panel, but note that the camera looks for QRCodes shown to it and attempts to retrieves the contents on the URL. Camera scanning is vulnerable to SSRF and can retrieve internal URLs. Grab contents of system panel and get code to the next combo lock.

## Challenge 3 - NFC Reader

Setup a vulnerable an NFC RFID reader that listens for specific UIDs and a piece of text stored on the tag/card that acts as a password. Return the correct information and the servo opens and light flashes green.

Light returns information based on the card you've scanned:

- Blue light = Waiting
- Red light = Wrong
- Orange light = Correct UID but wrong password
- Green light = Correct UID and correct password

## Bonus Challenges

There are two bonus challenges for those that pwn the entire Raspberry PI, each get an extra prize:

- A 'how_did_we_get_here.txt' flag in the root directory of the PI
- A secret second web application running on the PI that requires the user to pwn the PI and check out the running services.

# Installation

If you fancy spinning up your own version of the electronics I've tried my best to include the steps and some infographics for easy setup.

### Materials Required:

- Raspberry Pi 4
- Raspberry Pi camera
- RFID-RFC522 NFC reader
- Mifare Classic 1k 13.56Mhz card or fob
- Plug to socket jumper leads
- Heat shrink
- Micro servo
- 20m copper wire
- Braided wire wrap
- Materials to create three boxes of varying size
- RGB light strip
- Speaker with aux capabilities

https://github.com/ikarus23/MifareClassicTool
https://play.google.com/store/apps/details?id=de.syss.MifareClassicTool
https://randomnerdtutorials.com/raspberry-pi-mjpeg-streaming-web-server-picamera2/

### Install project and dependencies:

Connect to the Raspberry Pi and install this repo.

```bash
git clone git@github.com:Real4XoR/KawaiiCon-Box-CTF-2025.git && cd KawaiiCon-Box-CTF-2025
pip3 install -r requirements.txt
```

Wire up the bits. I've included a Raspberry Pi 4 pin-out sheet and the wiring setup that I used.

![Raspberry PI pin-out](images/GPIO.png)

![Box wiring](images/RaspberryPi-pinout.png)

# Prizes

- T-shirts
- Vouchers (TryHackMe (https://tryhackme.com/subscriptions), $17 p/month or HackTheBox, $20 USD p/month (https://www.hackthebox.com/giftcards))

# Credits

This is a continuation of Dunderhay's box project from 2019: https://github.com/dunderhay/Kawaiicon-Box-CTF-2019
