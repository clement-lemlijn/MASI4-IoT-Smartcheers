#!/usr/bin/env python3

import time
import grovepi

# Grove Light Sensor analog port A0
# SIG,NC,VCC,GND
light_sensor = 2

# LED to digital port D4
# SIG,NC,VCC,GND
led = 4

threshold = 10

grovepi.pinMode(light_sensor,"INPUT")
grovepi.pinMode(led,"OUTPUT")


def _get_resistance():
    """Retourne la résistance calculée du capteur."""
    sensor_value = grovepi.analogRead(light_sensor)

    # Évite une division par zéro
    if sensor_value <= 0:
        return float("inf")

    return (1023 - sensor_value) * 10.0 / sensor_value


def is_train_passing() -> bool:
    """Retourne True lorsque le train masque le capteur."""
    resistance = _get_resistance()

    print(f"Light sensor : {resistance:.2f} KΩ")

    return resistance > threshold

def wait_for_train(timeout_after_last_detection=5):
    """
    Attend le passage complet du train.

    La LED suit directement l'état du capteur.
    La fonction se termine lorsqu'il n'y a plus eu de détection
    depuis `timeout_after_last_detection` secondes.
    """

    print("En attente du train...")

    train_seen = False
    last_detection = None

    while True:
        detected = is_train_passing()

        # La LED reflète directement le capteur
        grovepi.digitalWrite(led, detected)

        if detected:
            if not train_seen:
                print("Premier passage détecté")
                train_seen = True

            last_detection = time.time()

        # Le train est considéré passé si plus aucune détection
        # depuis 5 secondes.
        if train_seen and (time.time() - last_detection) > timeout_after_last_detection:
            break

        time.sleep(0.05)

    grovepi.digitalWrite(led, 0)
    print("Train passé")