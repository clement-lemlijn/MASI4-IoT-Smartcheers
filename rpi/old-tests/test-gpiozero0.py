#!/usr/bin/env python3
"""
Remet le servo à 0°
"""

from gpiozero import AngularServo
from time import sleep

SERVO_PIN = 12
MIN_ANGLE = -90
MAX_ANGLE = 90
MIN_PULSE = 0.0005
MAX_PULSE = 0.0025

ANGLE_FERME = 0
ANGLE_OUVERT = 60

servo = AngularServo(
    SERVO_PIN,
    min_angle=MIN_ANGLE,
    max_angle=MAX_ANGLE,
    min_pulse_width=MIN_PULSE,
    max_pulse_width=MAX_PULSE
)

print("FERME")
servo.angle = ANGLE_FERME
sleep(5)

print("OUVERT")
servo.angle = ANGLE_OUVERT
sleep(1)

print("FERME")
servo.angle = ANGLE_FERME
sleep(1)

servo.detach()
print("détaché.")
