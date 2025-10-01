# KawaiiCon-Box-CTF-2025

# Overview

A challenge box for KawaiiCon 2025. Solve the riddles, get a prize.

Overall cost: $XXX

## Challenge 1 - Padlock Riddle

There are two ways to open the box - either you solve the puzzle and get the combo lock code or you pick the other lock. Both open the first box. 

#### Puzzle

eight locks with 35 keys

locks attached to chain 

only three keys work

all locks have letters on them 

all keys have ROT-X letters on them

letter correspond with the number of its place in alphabet e.g. A=1 B=2 ... Z=26

correct 3 digits will unlock combo pad lock

## Challnge 2 - Smart Camera

Have a local web server hosted on a Pi 4. Vulnerable login portal (SQLI), gets redirected to dashboard with loads of local IP addresses. One of them leads to the actuial camera in the box. Camera is looking at QR code that contains information on how to get code for the combo lock.



## Challenge 3 - NFC Cracking

Setup a vulnerable NFC reader with a crap password or magic code. Let users try and crack it or read it off an existing card.



# Installation

If you fancy spinning up your own version of the electronics I've tried my best to include the steps and some infographics for easy setup.

#### Materials Required:

- Raspberry Pi 4
- Raspberry Pi camera
- RFID-RFC522 NFC reader
- Plug to socket jumper leads
- Heat shrink
- Mifare Classic 1k 13.56Mhz card or fob
- Micro servo
- 

https://github.com/ikarus23/MifareClassicTool
https://play.google.com/store/apps/details?id=de.syss.MifareClassicTool
https://randomnerdtutorials.com/raspberry-pi-mjpeg-streaming-web-server-picamera2/

#### Install project and dependencies:

```bash
git clone git@github.com:Real4XoR/KawaiiCon-Box-CTF-2025.git && cd KawaiiCon-Box-CTF-2025
pip3 install -r requirements.txt
```

Wire up the bits. I've included a Raspberry Pi 4 pin-out sheet and the wiring setup that I used.

![Raspberry PI pin-out](images/GPIO.png)

![Box wiring](images/Box-Pinout.png)

# Prizes

- T-shirts
- Vouchers (TryHackMe (https://tryhackme.com/subscriptions), $17 p/month or HackTheBox, $20 USD p/month (https://www.hackthebox.com/giftcards))

# Credits

This is a continuation of Dunderhay's box project from 2019: https://github.com/dunderhay/Kawaiicon-Box-CTF-2019
