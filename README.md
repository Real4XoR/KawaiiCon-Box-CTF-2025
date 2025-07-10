# KawaiiCon-Box-CTF-2025

# Overview

A challenge box for KawaiiCon 2025. Solve the riddles, get a prize.

Overall cost: $XXX

## Challenge 1 - Padlock Riddle

First box contains multiple locks on a rod with loads on keys that could open any one of them. Riddle to find four keys with numbers on them to unlock combo lock.

#### Riddles

TODO

#### Materials Required:

- Combo lock

## Challnge 2 - Smart Camera

Have a local web server hosted on a Pi 4. Vulnerable login portal (SQLI), gets redirected to dashboard with loads of local IP addresses. One of them leads to the actuial camera in the box. Camera is looking at QR code that contains information on how to get code for the combo lock.

#### Materials Required:

- Raspberry Pi 4
- Raspberry Pi Camera (https://www.digikey.co.nz/en/products/detail/raspberry-pi/SC1223/17278639)
- Combo lock
- https://randomnerdtutorials.com/raspberry-pi-mjpeg-streaming-web-server-picamera2/

## Challenge 3 - NFC Cracking

Setup a vulnerable NFC reader with a crap password or magic code. Let users try and crack it or read it off an existing card.

#### Materials Required:

- NFC reader
- Programmable 125kHz RFID card
- Bad password or UID
- Servo
- https://github.com/ikarus23/MifareClassicTool
- https://play.google.com/store/apps/details?id=de.syss.MifareClassicTool

# Prizes

- T-shirts
- Vouchers (TryHackMe (https://tryhackme.com/subscriptions), $17 p/month or HackTheBox, $20 USD p/month (https://www.hackthebox.com/giftcards))

# Credits

This is a continuation of Dunderhay's box project from 2019: https://github.com/dunderhay/Kawaiicon-Box-CTF-2019
