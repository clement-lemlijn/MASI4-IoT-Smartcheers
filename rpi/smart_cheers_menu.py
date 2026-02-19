import time
import grovepi
import RPi.GPIO as GPIO
import paho.mqtt.client as paho
import time
from pymongo import MongoClient
from grove_rgb_lcd import *

# --- CONFIG MQTT ---
broker_ip = "192.168.68.75"
broker_port = 1883
mqtt_topic = "smartcheers"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)

def on_publish(client, userdata, mid):
    print("Message published")

def mqtt_publish(payload):
    client = paho.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker_ip, broker_port, 60)
    client.loop_start()
    client.publish(mqtt_topic, payload)
    time.sleep(1)
    client.loop_stop()
    client.disconnect()

# --- CONFIG ---
JOYSTICK_X = 0  # A0
JOYSTICK_Y = 1  # A1
SW_GPIO = 17    # Bouton joysticj

Y_UP = 300
Y_DOWN = 700
X_LEFT = 300

# --- GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(SW_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- MENUS ---
MAIN_MENU = ["Boissons", "Snacks"]
DRINKS = ["Coca", "Fanta", "Sprite", "Bière"]
SNACKS = ["Chips", "Saucisson", "Pizza"]

menu_stack = [MAIN_MENU]
index = 0

# --- LCD ---
setRGB(0, 128, 100)

def display_menu(menu, idx):
    setText(f"> {menu[idx]}\n  {menu[(idx+1)%len(menu)]}")

def read_joystick():
    x = grovepi.analogRead(JOYSTICK_X)
    y = grovepi.analogRead(JOYSTICK_Y)
    sw = GPIO.input(SW_GPIO)
    return x, y, sw

display_menu(menu_stack[-1], index)

try:
    while True:
        x, y, sw = read_joystick()

        # Navigation BAS
        if y > Y_DOWN:
            index = (index + 1) % len(menu_stack[-1])
            display_menu(menu_stack[-1], index)
            time.sleep(0.3)

        # Navigation HAUT
        elif y < Y_UP:
            index =  (index - 1) % len(menu_stack[-1])
            display_menu(menu_stack[-1], index)
            time.sleep(0.3)

        # RETOUR
        elif x < X_LEFT and len(menu_stack) > 1:
            menu_stack.pop()
            index = 0
            display_menu(menu_stack[-1], index)
            time.sleep(0.3)

        # VALIDATION
        elif sw == 0:
            choice = menu_stack[-1][index]

            if choice == "Boissons":
                menu_stack.append(DRINKS)
                index = 0
                display_menu(DRINKS, index)

            elif choice == "Snacks":
                menu_stack.append(SNACKS)
                index = 0
                display_menu(SNACKS, index)

            else:
                setRGB(0, 255, 0)
                setText(f"Commande:\n{choice}")
                print(f"Commande envoyée : {choice}")
                mqtt_publish(f"Commande envoyée : {choice}")
                time.sleep(2)
                setRGB(0, 128, 255)
                display_menu(menu_stack[-1], index)

            time.sleep(0.3)

        time.sleep(0.05)


except KeyboardInterrupt:
    setText("Arrêt")
    setRGB(255, 0, 0)

finally:
    GPIO.cleanup()
