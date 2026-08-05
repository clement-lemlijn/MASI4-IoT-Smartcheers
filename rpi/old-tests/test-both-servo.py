#!/usr/bin/env python3
"""
Test au démarrage - 2 servos
- Rail     → GPIO 12
- Barrière → GPIO 13
"""

from gpiozero import AngularServo
from time import sleep

# === Configuration ===
PIN_RAIL     = 12
PIN_BARRIERE = 13

MIN_ANGLE = -90
MAX_ANGLE = 90
MIN_PULSE = 0.0005
MAX_PULSE = 0.0025

# Création des deux servos
servo_rail = AngularServo(
    PIN_RAIL,
    min_angle=MIN_ANGLE,
    max_angle=MAX_ANGLE,
    min_pulse_width=MIN_PULSE,
    max_pulse_width=MAX_PULSE
)

servo_barriere = AngularServo(
    PIN_BARRIERE,
    min_angle=MIN_ANGLE,
    max_angle=MAX_ANGLE,
    min_pulse_width=MIN_PULSE,
    max_pulse_width=MAX_PULSE
)

def set_angle(servo, angle, name):
    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))
    servo.angle = angle
    print(f"{name:10} → {angle:6.1f}°")

try:
    print("=== Test démarrage des 2 servos ===")
    print("Rail (GPIO 12) + Barrière (GPIO 13)\n")

    # 1. Remise à 0 des deux
    print("--- Position 0° ---")
    set_angle(servo_rail, 0, "Rail")
    set_angle(servo_barriere, 0, "Barrière")
    sleep(1.5)

    # 2. Rail va à +90, Barrière va à -90
    print("\n--- Mouvement 1 ---")
    set_angle(servo_rail, 90, "Rail")
    set_angle(servo_barriere, -90, "Barrière")
    sleep(1.5)

    # 3. Rail va à -90, Barrière va à +90
    print("\n--- Mouvement 2 ---")
    set_angle(servo_rail, -90, "Rail")
    set_angle(servo_barriere, 90, "Barrière")
    sleep(1.5)

    # 4. Retour à 0
    print("\n--- Retour à 0° ---")
    set_angle(servo_rail, 0, "Rail")
    set_angle(servo_barriere, 0, "Barrière")
    sleep(1.5)

    print("\nTest terminé avec succès.")

except KeyboardInterrupt:
    print("\nArrêt demandé...")

finally:
    servo_rail.detach()
    servo_barriere.detach()
    print("Les deux servos sont détachés.")
