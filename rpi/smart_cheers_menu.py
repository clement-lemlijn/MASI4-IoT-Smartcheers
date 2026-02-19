import time
import grovepi
import RPi.GPIO as GPIO
import paho.mqtt.client as paho
from grove_rgb_lcd import *
import serial
import json

# --- CONFIG MQTT ---
broker_ip = "192.168.68.77"
broker_port = 1883
mqtt_topic = "smartcheers/order/create"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)

def on_publish(client, userdata, mid):
    print("Message published")

def mqtt_publish(payload):
    client = paho.Client(client_id="smartcheers-pub-001")
    client.username_pw_set(username="rpi-001",password='29!pSubG')
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker_ip, broker_port, 60)
    client.loop_start()
    client.publish(mqtt_topic, payload)
    time.sleep(1)
    client.loop_stop()
    client.disconnect()

# --- CONFIG MQTT livraison ---
deliver_topic = "smartcheers/order/deliver"
delivery_received = False
delivered_by = None

def on_message(client, userdata, msg):
    global delivery_received, delivered_by
    try:
        payload = json.loads(msg.payload.decode())
        employee_id = payload.get("employeeId")
        print(f"Commande livrée par le serveur {employee_id}")
        delivered_by = employee_id
        delivery_received = True
    except Exception as e:
        print("Erreur lors du traitement de la livraison :", e)

def start_mqtt_listener():
    client = paho.Client(client_id="smartcheers-sub-001")
    client.username_pw_set(username='rpi-001',password='29!pSubG')
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_ip, broker_port, 60)
    client.subscribe(deliver_topic)
    client.loop_start()
    return client

# --- CONFIG Joystick ---
JOYSTICK_X = 0  # A0
JOYSTICK_Y = 1  # A1
SW_GPIO = 17    # Bouton joystick

Y_UP = 300
Y_DOWN = 700
X_LEFT = 300
X_RIGHT = 700  # Pour basculer vers le panier

GPIO.setmode(GPIO.BCM)
GPIO.setup(SW_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- MENUS ---
MAIN_MENU = ["Boissons", "Snacks", "Confirmer"]
DRINKS = ["Coca", "Fanta", "Sprite", "Biere"]
SNACKS = ["Chips", "Saucisson", "Pizza"]

menu_stack = [MAIN_MENU]
index = 0

# --- LCD ---
setRGB(0, 128, 100)

def format_item(item, panier):
    """Retourne le texte formaté avec la quantité à droite"""
    qty = panier.get(item, 0)
    # Espace restant = 16 - longueur nom - longueur xN
    txt = f"{item}"
    suffix = f"x{qty}" if qty > 0 else ""
    espace = 14 - len(txt) - len(suffix)
    return f"{txt}{' '*espace}{suffix}"

def display_menu(menu, idx, panier):
    """Affiche le menu avec quantité à droite"""
    item1 = format_item(menu[idx], panier)
    item2 = format_item(menu[(idx+1)%len(menu)], panier)
    setText(f"> {item1}\n  {item2}")

def display_panier(panier):
    """Affiche le panier de façon compacte"""
    if not panier:
        setText("Panier vide")
        return
    lignes = []
    ligne = ""
    for produit, quantite in panier.items():
        abr = f"{produit[0]}:{quantite}"  # Ex: 'C:2' pour Coca 2
        if len(ligne) + len(abr) + 1 <= 16:
            ligne += " " + abr if ligne else abr
        else:
            lignes.append(ligne)
            ligne = abr
    lignes.append(ligne)
    setText("\n".join(lignes[:2]))

def read_joystick():
    x = grovepi.analogRead(JOYSTICK_X)
    y = grovepi.analogRead(JOYSTICK_Y)
    sw = GPIO.input(SW_GPIO)
    return x, y, sw

# --- RFID ---
ser = serial.Serial(port='/dev/serial0', baudrate=9600, timeout=1)

def wait_for_rfid():
    setRGB(255, 255, 0)
    setText("Scannez votre badge")
    print("🟢 En attente d'un badge RFID...")
    while True:
        data = ser.read(14)
        if data:
            try:
                badge_id = data.decode('ascii', errors='ignore').strip()
                if badge_id:
                    print("📟 Badge détecté :", badge_id)
                    setRGB(0, 255, 0)
                    setText(f"Bienvenue !\nID:{badge_id}")
                    time.sleep(2)
                    return badge_id
            except Exception as e:
                print("Erreur :", e)

# --- MAIN ---
try:
    while True:
        client_id = wait_for_rfid()
        index = 0
        menu_stack = [MAIN_MENU]
        panier = {}
        show_panier = False
        display_menu(menu_stack[-1], index, panier)

        commande_terminee = False
        while not commande_terminee:
            x, y, sw = read_joystick()

            # Bascule écran menu / panier
            if x > X_RIGHT:
                show_panier = True
                display_panier(panier)
                time.sleep(0.3)
            elif x < X_LEFT:
                show_panier = False
                display_menu(menu_stack[-1], index, panier)
                time.sleep(0.3)

            if not show_panier:
                # Navigation BAS
                if y > Y_DOWN:
                    index = (index + 1) % len(menu_stack[-1])
                    display_menu(menu_stack[-1], index, panier)
                    time.sleep(0.3)

                # Navigation HAUT
                elif y < Y_UP:
                    index = (index - 1) % len(menu_stack[-1])
                    display_menu(menu_stack[-1], index, panier)
                    time.sleep(0.3)

                # RETOUR
                elif x < X_LEFT and len(menu_stack) > 1:
                    menu_stack.pop()
                    index = 0
                    display_menu(menu_stack[-1], index, panier)
                    time.sleep(0.3)

                # VALIDATION
                elif sw == 0:
                    choice = menu_stack[-1][index]

                    if choice == "Boissons":
                        menu_stack.append(DRINKS)
                        index = 0
                        display_menu(DRINKS, index, panier)

                    elif choice == "Snacks":
                        menu_stack.append(SNACKS)
                        index = 0
                        display_menu(SNACKS, index, panier)

                    elif choice == "Confirmer":
                        if panier:
                            # Affichage de la page de confirmation abrégée
                            setRGB(255, 255, 0)
                            setText("Confirmer ?\n")
                            display_panier(panier)
                            time.sleep(0.5)
                            confirmation = False
                            while not confirmation:
                                x_c, y_c, sw_c = read_joystick()
                                # Bouton validation = confirmer
                                if sw_c == 0:
                                    payload = json.dumps({
                                        "clientUid": client_id,
                                        "command": [{"produit": k, "quantite": v} for k, v in panier.items()]
                                    })
                                    print(f"Commande envoyée : {payload}")
                                    mqtt_publish(payload)
                                    setRGB(0, 255, 0)
                                    setText("Commande envoyee")
                                    time.sleep(2)
                                    confirmation = True
                                    commande_terminee = True

                                    # Commande envoyée
                                    setRGB(255, 165, 0)
                                    setText("En attente de   livraison")

                                    # Démarrer le listener MQTT
                                    mqtt_client = start_mqtt_listener()

                                    # Boucle d'attente active : on continue de scanner le badge
                                    while not delivery_received:
                                        badge_id = ser.read(14)
                                        if badge_id:
                                            try:
                                                badge_id = badge_id.decode('ascii', errors='ignore').strip()
                                                if badge_id:
                                                    print(f"Badge rescanne : {badge_id}")
                                                    # Considérer la livraison effectuée
                                                    delivered_by = badge_id
                                                    delivery_received = True
                                            except:
                                                passw
                                        time.sleep(0.1)

                                    # Afficher livraison et revenir à l'accueil
                                    setRGB(0, 128, 255)
                                    setText(f"Livre par :\n{delivered_by}")
                                    time.sleep(3)
                                    setRGB(0, 128, 100)
                                    setText("Pret pour nouvelle commande")
                                    time.sleep(1)

                                    # Arrêter MQTT
                                    mqtt_client.loop_stop()
                                    mqtt_client.disconnect()

                                # Joystick à gauche = annuler confirmation
                                elif x_c < X_LEFT:
                                    display_menu(menu_stack[-1], index, panier)
                                    confirmation = True
                                    break
                                time.sleep(0.05)
                        else:
                            setRGB(255, 0, 0)
                            setText("Panier vide !")
                            time.sleep(2)
                            commande_terminee = True

                    else:
                        # Ajoute ou incrémente le produit dans le panier
                        panier[choice] = panier.get(choice, 0) + 1
                        display_menu(menu_stack[-1], index, panier)

                    time.sleep(0.3)

            time.sleep(0.05)

except KeyboardInterrupt:
    setText("Arrêt")
    setRGB(255, 0, 0)

finally:
    GPIO.cleanup()
