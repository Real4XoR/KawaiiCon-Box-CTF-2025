import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# ---------- CONFIG ----------

magic_uid = "7481b8c885"     # Expected UID
magic_password = "wootwoot"  # Expected password

pins = {'pin_R': 17, 'pin_G': 22, 'pin_B': 27}

FREQ_R = 2000
FREQ_G = 2000
FREQ_B = 5000

COLOR_BLUE   = 0x0000FF   
COLOR_GREEN  = 0x00FF00   
COLOR_RED    = 0xFF0000   
COLOR_TEAL   = 0xB2D8D8   

OPEN_STATE = 90
CLOSE_STATE = -90

# ---------- GPIO / PWM setup ----------

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

# ---------- Servo Control ----------------

factory = PiGPIOFactory()
servo = AngularServo(18, min_pulse_width=0.0005, max_pulse_width=0.0024, pin_factory=factory)

def open_door():
	servo.angle = OPEN_STATE

def close_door():
	servo.angle = CLOSE_STATE

# ---------- RFID reader ----------

reader = SimpleMFRC522()

def format_uid_as_hex(uid_int):
    """
    Convert integer UID returned by SimpleMFRC522 to lowercase hex string
    without 0x prefix. Zero-pad to even length if needed.
    """
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

# ---------- Main loop ----------

if __name__ == "__main__":
    print("Expected UID:    ", magic_uid)
    print("Expected secret: ", magic_password)
    print("Waiting for tag. Use Ctrl+C to quit.\n")

    try:
        while True:
            set_color(COLOR_BLUE)
            print("Place a tag on the reader...")
            uid_int, data = reader.read() 
            uid_hex = format_uid_as_hex(uid_int) # Convert UID to hex
            read_text = (data or "").strip()

            print("Detected UID (int):", uid_int)
            print("Detected UID (hex):", uid_hex)
            print("Stored text on tag:", repr(read_text))

            if uid_hex == magic_uid.lower():
                if read_text == magic_password:
                    print(">> SUCCESS: UID and password match.")
                    set_color(COLOR_GREEN)
                    open_door()
                else:
                    print(">> WARNING: UID matches but password is incorrect.")
                    set_color(COLOR_TEAL)
                time.sleep(2)
            else:
                print(">> FAIL: UID does not match expected value.")
                set_color(COLOR_RED)
                close_door()
                time.sleep(2)

            set_color(COLOR_BLUE)
            print("\nReady for next card.\n")
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\nExiting (KeyboardInterrupt). Cleaning up GPIO...")
    except Exception as e:
        print("\nAn error occurred:", e)
    finally:
        cleanup()
        print("Cleanup done. Goodbye.")