import RPi.GPIO as GPIO
import pygame, os, time
from mfrc522 import SimpleMFRC522
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
from gpiozero import Button

button = Button(6)  # GPIO 6

def on_button_press():
    print("Button pressed! Playing music...")
    play_music("wow.wav")  # Replace with your file name

# --- Connect button event ---
button.when_pressed = on_button_press

print("Ready. Press the button to play music.")


# ---------- Config ----------

# expected UID (as hex string, lowercase, no "0x", zero-padded as needed)
magic_uid = "7481b8c885"

# expected password (text stored on the tag)
magic_password = "wootwoot1"

dir = os.path.dirname(__file__)
pygame.mixer.init()
pygame.mixer.music.set_volume(1)

# ----------------------------

# RGB pins (BCM)
pins = {'pin_R': 17, 'pin_G': 22, 'pin_B': 27}

# PWM frequencies
FREQ_R = 2000
FREQ_G = 2000
FREQ_B = 5000

# Colors used (hex)
COLOUR_BLUE   = 0x0000FF   # waiting
COLOUR_GREEN  = 0x00FF00   # success
COLOUR_RED    = 0xFF0000   # uid mismatch / failure
COLOUR_PURPLE = 0x800080   # uid match but wrong password

GPIO.setmode(GPIO.BCM)

for key in pins:
    GPIO.setup(pins[key], GPIO.OUT)
    GPIO.output(pins[key], GPIO.HIGH)  # Use HIGH for common cathode LEDs (LOW for common anode)

p_R = GPIO.PWM(pins['pin_R'], FREQ_R)
p_G = GPIO.PWM(pins['pin_G'], FREQ_G)
p_B = GPIO.PWM(pins['pin_B'], FREQ_B)

p_R.start(0)
p_G.start(0)
p_B.start(0)

# ---------- Helper Functions ----------

def map_val(x, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another."""
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def set_color(hex_color):
    """Set LED color using a 24-bit hex value (e.g. 0xFFA500 for orange)."""
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
    """Turns the LED off."""
    set_color(COLOR_OFF)

# ---------- Button ----------

button = Button(6)  # GPIO 6

def on_button_press():
    print("Button pressed! Playing music...")
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

def play_music(music_file):
    pygame.mixer.music.stop()
    file_path = os.path.join("/home/raspberry/kawaiicon_box/static", music_file)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# ---------- RFID reader ----------

reader = SimpleMFRC522()

def format_uid_as_hex(uid_int):
    """
    Convert integer UID returned by SimpleMFRC522 to lowercase hex string
    without 0x prefix. Zero-pad to even length if needed.
    """
    h = format(uid_int, 'x').lower()
    # optional: zero-pad to a consistent length if you know it (e.g. 10)
    # h = h.zfill(10)
    return h

def cleanup():
    try:
        p_R.stop()
        p_G.stop()
        p_B.stop()
    except Exception:
        pass
    # turn off LEDs (set HIGH if wiring is active-low)
    for key in pins:
        try:
            GPIO.output(pins[key], GPIO.HIGH)
        except Exception:
            pass
    GPIO.cleanup()

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
            # show waiting color
            set_color(COLOUR_BLUE)
            # reader.read() blocks until a tag is presented
            print("Place a tag on the reader...")
            uid_int, data = reader.read()   # id (int), text (str)
            uid_hex = format_uid_as_hex(uid_int)
            read_text = (data or "").strip()

            print("Detected UID (int):", uid_int)
            print("Detected UID (hex):", uid_hex)
            print("Stored text on tag:", repr(read_text))

            if uid_hex == magic_uid.lower():
                # UID matches
                if read_text == magic_password:
                    print(">> SUCCESS: UID and password match.")
                    set_color(COLOUR_GREEN)
                    play_music("wow.wav")
                    open_door()
                else:
                    print(">> WARNING: UID matches but password is incorrect.")
                    set_color(COLOUR_PURPLE)
                # hold feedback for 2 seconds so it is noticeable
                time.sleep(2)
            else:
                # UID does not match
                print(">> FAIL: UID does not match expected value.")
                set_color(COLOUR_RED)
                close_door()
                time.sleep(2)

            # after feedback, go back to waiting color for the next tag
            set_color(COLOUR_BLUE)
            print("\nReady for next card.\n")
            # small delay to avoid bouncing immediate re-reads
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\nExiting (KeyboardInterrupt). Cleaning up GPIO...")
    except Exception as e:
        print("\nAn error occurred:", e)
    finally:
        cleanup()
        print("Cleanup done. Goodbye.")
