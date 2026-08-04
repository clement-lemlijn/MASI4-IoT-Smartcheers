"""Lecture du joystick analogique Grove + bouton poussoir intégré."""
import RPi.GPIO as GPIO
import grovepi

JOYSTICK_X = 0  # A0
JOYSTICK_Y = 1  # A1
SW_GPIO = 17    # Bouton joystick (câblé directement sur un GPIO du RPi)

Y_UP = 300
Y_DOWN = 700
X_LEFT = 300
X_RIGHT = 700  # Pour basculer vers le panier


def setup_joystick():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SW_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def read_joystick():
    x = grovepi.analogRead(JOYSTICK_X)
    y = grovepi.analogRead(JOYSTICK_Y)
    sw = GPIO.input(SW_GPIO)
    return x, y, sw