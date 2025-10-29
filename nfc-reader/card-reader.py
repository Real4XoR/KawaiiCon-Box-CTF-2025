import os
import io
import time
import wave
import threading
from time import sleep

import pygame
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from gpiozero import AngularServo, Button
from gpiozero.pins.pigpio import PiGPIOFactory

GPIO.setwarnings(False)

# ---------- Config ----------

# expected UID
magic_uid = "7481b8c885"

# expected password
magic_password = "DieHardIsAChristmasMovie"

dir = os.path.dirname(__file__)
pygame.mixer.init()
pygame.mixer.music.set_volume(1)

# ----------------------------

pins = {'pin_R': 17, 'pin_G': 27, 'pin_B': 22}

FREQ_R = 2000
FREQ_G = 2000
FREQ_B = 5000

COLOUR_BLUE   = 0x0000FF   # waiting
COLOUR_GREEN  = 0x00FF00   # success
COLOUR_RED    = 0xFF0000   # uid mismatch / failure
COLOUR_PURPLE = 0x800080   # uid match but wrong password
COLOUR_OFF    = 0x000000   # turn off

GPIO.setmode(GPIO.BCM)

for key in pins:
    GPIO.setup(pins[key], GPIO.OUT)
    GPIO.output(pins[key], GPIO.HIGH) 

p_R = GPIO.PWM(pins['pin_R'], FREQ_R)
p_G = GPIO.PWM(pins['pin_G'], FREQ_G)
p_B = GPIO.PWM(pins['pin_B'], FREQ_B)

p_R.start(0)
p_G.start(0)
p_B.start(0)

# ---------- Helper Functions ----------

def map_val(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def set_color(hex_color):
    r = (hex_color & 0xFF0000) >> 16
    g = (hex_color & 0x00FF00) >> 8
    b = (hex_color & 0x0000FF)

    r_dc = map_val(r, 0, 255, 0, 100)
    g_dc = map_val(g, 0, 255, 0, 100)
    b_dc = map_val(b, 0, 255, 0, 100)

    p_R.ChangeDutyCycle(r_dc)
    p_G.ChangeDutyCycle(g_dc)
    p_B.ChangeDutyCycle(b_dc)

def turn_off():
    set_color(COLOR_OFF)

# ---------- Button ----------

button = Button(6)

def on_button_press():
    play_music("wow.wav") 

button.when_pressed = on_button_press

# ---------- Servo ----------------

factory = PiGPIOFactory()
servo = AngularServo(18, min_pulse_width=0.0005, max_pulse_width=0.0024, pin_factory=factory)

def open_door():
	servo.angle = 90

def close_door():
	servo.angle = -90

# ---------- Music ---------------

'''
def keep_speaker_alive(interval=120):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as f:
        f.setnchannels(2)     
        f.setsampwidth(2)      
        f.setframerate(44100)
        f.writeframes(b'\x00' * 4410 * 2 * 2) 
    buf.seek(0)

    sound = pygame.mixer.Sound(buffer=buf)

    while True:
        sound.play()
        time.sleep(interval)
'''

def play_music(music_file):
    pygame.mixer.music.stop()
    file_path = os.path.join("./nfc-reader/static", music_file)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# ---------- RFID reader ----------

reader = SimpleMFRC522()

def format_uid_as_hex(uid_int):
    h = format(uid_int, 'x').lower()
    return h

def cleanup():
    try:
        p_R.stop()
        p_G.stop()
        p_B.stop()
    except Exception:
        pass
    for key in pins:
        try:
            GPIO.output(pins[key], GPIO.HIGH)
        except Exception:
            pass
    GPIO.cleanup()

    def cleanup_reader(reader):
    try:
        if hasattr(reader, "READER") and hasattr(reader.READER, "Close_MFRC522"):
            reader.READER.Close_MFRC522()
            print("MFRC522 SPI connection closed.")
    except Exception as e:
        print("Warning: could not close reader cleanly:", e)

def normalize_card_text(data):
    if data is None:
        return ""
    if isinstance(data, str):
        b = data.encode('utf-8', errors='ignore')
    elif isinstance(data, bytes):
        b = data
    else:
        b = str(data).encode('utf-8', errors='ignore')

    b = b.rstrip(b'\x00')
    return b.decode('utf-8', errors='ignore')

# ---------- Main loop ----------

if __name__ == "__main__":
    print("MIFARE Check Script")
    print("Expected UID:    ", magic_uid)
    print("Expected secret: ", magic_password)
    print("Closing door")
    print("Waiting for tag. Use Ctrl+C to quit.\n")

    close_door()

    try:
        while True:
            # ✅ Create reader each loop iteration (ensures SPI reinit each time)
            reader = SimpleMFRC522()
            set_color(COLOUR_BLUE)
            print("Place a tag on the reader...")

            uid_int, data = reader.read()
            uid_hex = format_uid_as_hex(uid_int)
            read_text = normalize_card_text(data)

            print("Detected UID (int):", uid_int)
            print("Detected UID (hex):", uid_hex)
            print("Stored text on tag:", repr(read_text))

            if uid_hex == magic_uid.lower():
                if read_text == magic_password:
                    print(">> SUCCESS: UID and password match.")
                    set_color(COLOUR_GREEN)
                    play_music("open.wav")
                    open_door()
                else:
                    print(">> WARNING: UID matches but password is incorrect.")
                    set_color(COLOUR_PURPLE)
                time.sleep(2)
            else:
                print(">> FAIL: UID does not match expected value.")
                set_color(COLOUR_RED)
                close_door()
                time.sleep(2)

            set_color(COLOUR_BLUE)
            print("\nReady for next card.\n")

            cleanup_reader(reader)
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\nExiting (KeyboardInterrupt). Cleaning up GPIO...")
    except Exception as e:
        print("\nAn error occurred:", e)
    finally:
        cleanup()
        print("Cleanup done. Goodbye.")
