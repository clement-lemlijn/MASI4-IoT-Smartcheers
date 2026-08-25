#!/usr/bin/env python3

import time
import grovepi
from grove_rgb_lcd_v5 import setText
from config import RPI_ID
from mqtt_client import mqtt_publish_train_passing
from actuators.rpiLoRa import send_train_passed

# Grove Light Sensor analog port A0
light_sensor = 2

# LED to digital port D4
led = 4

# Buzzer to digital port D8
buzzer = 8

threshold = 10

grovepi.pinMode(light_sensor, "INPUT")
grovepi.pinMode(led, "OUTPUT")
grovepi.pinMode(buzzer, "OUTPUT")


def beep_buzzer(duration=2.0):
    """Emet un bip de 2 secondes lors de la détection du train."""
    grovepi.digitalWrite(buzzer, 1)
    time.sleep(duration)
    grovepi.digitalWrite(buzzer, 0)


def _get_resistance():
    """Retourne la résistance calculée du capteur."""
    sensor_value = grovepi.analogRead(light_sensor)
    if sensor_value <= 0:
        return float("inf")
    return (1023 - sensor_value) * 10.0 / sensor_value


def is_train_passing() -> bool:
    """Retourne True lorsque le train masque le capteur."""
    return _get_resistance() > threshold


def wait_for_train():
    """
    Attend le passage du train.
    - Allume la lampe à chaque détection
    - Publie un message MQTT au premier passage
    - Met à jour l'écran LCD (une fois)
    """
    print("En attente du train...")
    
    train_detected = False
    last_detection = None
    timeout_after_last_detection = 5

    while True:
        detected = is_train_passing()
        
        # Allumer la lampe si train détecté
        grovepi.digitalWrite(led, 1 if detected else 0)

        if detected:
            if not train_detected:
                print("🚂 Train détecté !")
                train_detected = True
                beep_buzzer()
                setText("Train passing...")
                
                # Publier le message MQTT une seule fois
                table_numero = int(RPI_ID.split("-")[-1])
                mqtt_publish_train_passing(table_numero)

                # Publier le message LoRa une seule fois
                send_train_passed()

            last_detection = time.time()

        # Train passé si plus de détection depuis 5 secondes
        if train_detected and (time.time() - last_detection) > timeout_after_last_detection:
            break

        time.sleep(0.05)

    grovepi.digitalWrite(led, 0)
    print("Train passé ✓")