import time
import grovepi
import RPi.GPIO as GPIO

# Axes (GrovePi)
JOYSTICK_X = 0  # A0
JOYSTICK_Y = 1  # A1

# Bouton (GPIO Raspberry)
SW_GPIO = 17  # GPIO17 = pin physique 11

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SW_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Joystick X/Y (Grove) + SW (GPIO)")

try:
    while True:
        x = grovepi.analogRead(JOYSTICK_X)
        y = grovepi.analogRead(JOYSTICK_Y)
        sw = GPIO.input(SW_GPIO)

        print(f"X:{x:4d} | Y:{y:4d} | SW:{sw}")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nArrêt")

finally:
    GPIO.cleanup()

