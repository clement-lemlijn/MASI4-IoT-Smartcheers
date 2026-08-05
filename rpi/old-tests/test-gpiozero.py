#!/usr/bin/env python3
"""
Contrôle d'un servo moteur sur Raspberry Pi (GrovePi compatible)
Utilise gpiozero + AngularServo
"""

from gpiozero import AngularServo
from time import sleep

# === Configuration ===
SERVO_PIN = 12          # Change selon le GPIO que tu utilises (BCM)
MIN_ANGLE = -90         # Ou 0 selon ton servo
MAX_ANGLE = 90          # Ou 180
MIN_PULSE = 0.0005      # 0.5 ms (ajuste si besoin)
MAX_PULSE = 0.0025      # 2.5 ms (ajuste si besoin)

# Création du servo
servo = AngularServo(
    SERVO_PIN,
    min_angle=MIN_ANGLE,
    max_angle=MAX_ANGLE,
    min_pulse_width=MIN_PULSE,
    max_pulse_width=MAX_PULSE
)

def set_angle(angle):
    """Place le servo à l'angle demandé"""
    # Limitation de sécurité
    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))
    servo.angle = angle
    print(f"Angle → {angle}°")

try:
    print("Contrôle du servo démarré (Ctrl+C pour quitter)")
    
    while True:
        # Exemple de mouvement
        set_angle(-90)
        sleep(1.5)
        
        set_angle(0)
        sleep(1.5)
        
        set_angle(90)
        sleep(1.5)
        
        set_angle(0)
        sleep(1.5)

except KeyboardInterrupt:
    print("\nArrêt demandé...")
finally:
    servo.detach()          # Relâche le servo (important)
    print("Servo détaché. Fin du programme.")
