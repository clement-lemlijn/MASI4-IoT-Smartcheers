"""Lecture du lecteur RFID (UART) : badge client et badge livreur."""
import time
import json
import serial

from grove_rgb_lcd_v5 import setText
from display import safe_setRGB
from leds import set_leds
from mqtt_client import mqtt_publish, DELIVER_ORDER_TOPIC

RFID_SERIAL_PORT = '/dev/serial0'
RFID_BAUDRATE = 9600

ser = serial.Serial(port=RFID_SERIAL_PORT, baudrate=RFID_BAUDRATE, timeout=1)


def wait_for_rfid():
    """Attend le scan du badge client et retourne son ID."""
    set_leds(blue=True)
    safe_setRGB(100, 150, 255)
    setText("Scannez votre badge")
    print("🟢 En attente d'un badge RFID...")
    while True:
        data = ser.read(14)
        if data:
            try:
                badge_id = data.decode('ascii', errors='ignore').strip()
                if badge_id:
                    print("📟 Badge détecté :", badge_id)
                    safe_setRGB(0, 255, 0)
                    setText(f"Bienvenue !\nID:{badge_id}")
                    time.sleep(2)
                    set_leds()
                    return badge_id
            except Exception as e:
                print("Erreur :", e)
        time.sleep(0.5)


# def wait_for_rfid_deliver(client_id):
#     """Attend le scan du badge de l'employé qui livre la commande."""
#     safe_setRGB(255, 165, 0)
#     setText("En attente de   livraison")
#     print("🟢 En attente d'un badge RFID...")
#     while True:
#         data = ser.read(14)
#         if data:
#             try:
#                 badge_id = data.decode('ascii', errors='ignore').strip()
#                 if badge_id:
#                     print("📟 Badge détecté :", badge_id)
#                     payload = json.dumps({
#                         "clientUid": client_id,
#                         "employeeUid": badge_id
#                     })
#                     mqtt_publish(payload, DELIVER_ORDER_TOPIC)
#                     safe_setRGB(0, 128, 255)
#                     setText(f"Livre par :\n{badge_id}")
#                     time.sleep(3)
#                     safe_setRGB(0, 128, 100)
#                     setText("Pret pour nouvelle commande")
#                     time.sleep(1)
#                     return badge_id
#             except Exception as e:
#                 print("Erreur :", e)
#         time.sleep(0.5)