import ssl
import time
import grovepi
import RPi.GPIO as GPIO
import paho.mqtt.client as paho
from grove_rgb_lcd import *
import serial
import json

# --- CONFIGURATION ---
broker_ip = "mqtt.smartcheers.local"
broker_port = 8883
mqtt_topic = "smartcheers/orders/new"
MQTT_USERNAME = "clement-lemlijn"
MQTT_PASSWORD = "mqtt-pwd"
payload = 'Commande envoyée : {"clientUid": "\u000227004228D09D\u0003", "command": [{"produit": "Coca", "quantite": 2}]}'

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker !")
        client.publish(mqtt_topic, payload)
    else:
        print(f"Échec connexion, code: {rc}")

def on_publish(client, userdata, mid):
    print("Message publié avec succès")

def mqtt_publish(payload):
    # Création du client
    client = paho.Client()
    client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
    client.tls_set(
        ca_certs="/home/pi/mqtt-certs/ca.crt",
        certfile="/home/pi/mqtt-certs/client.crt",
        keyfile="/home/pi/mqtt-certs/client.key",
        tls_version=ssl.PROTOCOL_TLSv1_2
    )

    client.on_connect = on_connect
    client.on_publish = on_publish

    print(f"Connexion au broker {broker_ip}:{broker_port}...")
    client.connect(broker_ip, broker_port, 60)

    client.loop_start()
    time.sleep(2)
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    mqtt_publish(payload)
