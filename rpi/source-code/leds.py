"""Gestion des 3 LEDs de statut (rouge/vert/bleu) branchées sur le GrovePi.

Sémantique utilisée dans le reste du projet :
- Bleu  : idle, en attente de badge
- Vert  : commande envoyée avec succès
- Rouge : erreur / annulation / timeout
"""
import time
import grovepi

LED_RED = 4    # D4
LED_GREEN = 3  # D3
LED_BLUE = 2   # D2


def setup_leds():
    for pin in (LED_RED, LED_GREEN, LED_BLUE):
        try:
            grovepi.pinMode(pin, "OUTPUT")
        except IOError:
            pass


def set_leds(red=False, green=False, blue=False):
    """Allume/éteint les 3 LEDs indépendamment. Tolérant aux erreurs I2C GrovePi."""
    for pin, state in ((LED_RED, red), (LED_GREEN, green), (LED_BLUE, blue)):
        try:
            grovepi.digitalWrite(pin, 1 if state else 0)
        except IOError:
            pass


def blink_led(color, times=3, delay=0.2):
    """color: 'red', 'green' ou 'blue'"""
    kwargs = {color: True}
    for _ in range(times):
        set_leds(**kwargs)
        time.sleep(delay)
        set_leds()
        time.sleep(delay)