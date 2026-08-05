#!/usr/bin/env python3

# actuators/servos.py

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
def set_servo_rail():
    return AngularServo(
        PIN_RAIL,
        min_angle=MIN_ANGLE,
        max_angle=MAX_ANGLE,
        min_pulse_width=MIN_PULSE,
    max_pulse_width=MAX_PULSE
)

def set_servo_barriere():
    return AngularServo(
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




def open_bifurcation():
    servo_rail = set_servo_rail()
    set_angle(servo_rail, 90, "Rail")
    sleep(2)
    servo_rail.detach()

def close_bifurcation():
    servo_rail = set_servo_rail()
    set_angle(servo_rail, 0, "Rail")
    sleep(2)
    servo_rail.detach()

def open_barrier():
    servo_barriere = set_servo_barriere()
    set_angle(servo_barriere, -90, "Barrière")
    sleep(2)
    servo_barriere.detach()

def close_barrier():
    servo_barriere = set_servo_barriere()
    set_angle(servo_barriere, 0, "Barrière")
    sleep(2)
    servo_barriere.detach()