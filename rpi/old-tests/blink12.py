#!/usr/bin/env python3
from gpiozero import LED
from time import sleep

LED_PIN = 18  # BCM

led = LED(LED_PIN)

try:
    print("Blink sur GPIO12 (Ctrl+C pour arrêter)")
    while True:
        led.on()
        print("LED ON")
        sleep(1)
        led.off()
        print("LED OFF")
        sleep(1)
except KeyboardInterrupt:
    print("Arrêt")
