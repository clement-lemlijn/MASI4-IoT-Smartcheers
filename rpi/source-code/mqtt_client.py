"""Publication MQTT sécurisée (TLS + certificats client/serveur) via Paho."""
import ssl
import time
import json
import paho.mqtt.client as paho
import threading

order_received = threading.Event()
order_ready = threading.Event()
order_preparation = threading.Event()
order_sent = threading.Event()
received_order_id = None

# Données de commande actuellement prête (pour envoyer au train)
current_ready_order = {
    "client_nom": "",
    "client_prenom": "",
    "lignes": [],  # Liste des items
}
from config import BROKER_IP, BROKER_PORT, MQTT_USERNAME, MQTT_PASSWORD

CREATE_ORDER_TOPIC = "smartcheers/orders/new"
ORDER_CREATED_TOPIC = "smartcheers/orders/created"
ORDER_RECEIVED_TOPIC = "smartcheers/orders/received"
ORDER_READY_TOPIC = "smartcheers/orders/ready"
ORDER_PREPARATION_TOPIC = "smartcheers/orders/preparation"
ORDER_SENT_TOPIC = "smartcheers/orders/envoyee"
DELIVER_ORDER_TOPIC = "smartcheers/orders/deliver"


CA_CERT = "/home/pi/mqtt-certs/ca.crt"
CLIENT_CERT = "/home/pi/mqtt-certs/client.crt"
CLIENT_KEY = "/home/pi/mqtt-certs/client.key"

# --- CHARGEMENT CONFIG ---
with open("../source-code/config.json", "r") as f:
    CONFIG = json.load(f)

RPI_ID = CONFIG["rpiId"]

def create_mqtt_client(client_id):
    client = paho.Client(client_id=client_id, protocol=paho.MQTTv311)

    client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
    client.tls_set(
        ca_certs=CA_CERT,
        certfile=CLIENT_CERT,
        keyfile=CLIENT_KEY,
        tls_version=ssl.PROTOCOL_TLSv1_2
    )
    return client



def mqtt_publish(payload, mqtt_topic):
    client = create_mqtt_client(f"smartcheers-pub-{int(time.time()*1000)}")
    try:
        client.connect(BROKER_IP, BROKER_PORT, 10)
        client.loop_start()
        client.publish(
            mqtt_topic,
            json.dumps(payload),
            qos=1
        )
        time.sleep(0.5)
        client.loop_stop()
        client.disconnect()
        # print("✅ Message envoyé")
        return True

    except Exception as e:
        print(f"❌ Erreur MQTT : {e}")
        return False


def on_order_created(client, userdata, msg):
    global received_order_id

    try:
        payload = json.loads(msg.payload.decode())
        if payload["rpiId"] != RPI_ID or payload["success"] == False:
            return
        received_order_id = payload["orderId"]
        print(f"📦 Commande reçue : {received_order_id}")
        order_received.set()

    except Exception as e:
        print(f"Erreur réception MQTT : {e}")

def on_order_preparation(client, userdata, msg):
    global received_order_id
    try:
        payload = json.loads(msg.payload.decode())
        print("Message préparation reçu :", payload)
        if payload.get("orderId") != received_order_id:
            print(f"orderId différent ({payload.get('orderId')} != {received_order_id})")
            return
        print(f"🔨 Commande en préparation : {received_order_id}")
        order_preparation.set()
    except Exception as e:
        print(f"Erreur réception MQTT (preparation) : {e}")

def on_order_ready(client, userdata, msg):
    global received_order_id, current_ready_order
    try:
        payload = json.loads(msg.payload.decode())
        print("Message ready reçu :", payload)
        if payload.get("orderId") != received_order_id:
            print(f"orderId différent ({payload.get('orderId')} != {received_order_id})")
            return
        
        # Stocker les données complètes de la commande
        current_ready_order["client_nom"] = payload.get("client", {}).get("nom", "Client")
        current_ready_order["client_prenom"] = payload.get("client", {}).get("prenom", "")
        current_ready_order["lignes"] = payload.get("lignes", [])
        
        print(f"✅ Commande prête : {received_order_id}")
        print(f"   Client : {current_ready_order['client_prenom']} {current_ready_order['client_nom']}")
        print(f"   Items : {len(current_ready_order['lignes'])} produit(s)")
        
        order_ready.set()
    except Exception as e:
        print(f"Erreur réception MQTT (ready) : {e}")

def on_order_sent(client, userdata, msg):
    global received_order_id
    try:
        payload = json.loads(msg.payload.decode())
        print("Message envoyé reçu :", payload)
        if payload.get("orderId") != received_order_id:
            print(f"orderId différent ({payload.get('orderId')} != {received_order_id})")
            return
        print(f"🚂 Commande envoyée : {received_order_id}")
        order_sent.set()
    except Exception as e:
        print(f"Erreur réception MQTT (envoyee) : {e}")

def mqtt_listen_orders_creation():
    client = create_mqtt_client(f"smartcheers-sub-created-{int(time.time()*1000)}")
    client.on_message = on_order_created
    client.connect(BROKER_IP, BROKER_PORT, 10)
    client.subscribe(
        "smartcheers/orders/created",
        qos=1
    )
    client.loop_start()
    return client

def mqtt_listen_orders_preparation():
    client = create_mqtt_client(f"smartcheers-sub-prep-{int(time.time()*1000)}")
    client.on_message = on_order_preparation
    client.connect(BROKER_IP, BROKER_PORT, 10)
    client.subscribe(
        ORDER_PREPARATION_TOPIC,
        qos=1
    )
    client.loop_start()
    return client

def mqtt_listen_orders_ready():
    client = create_mqtt_client(f"smartcheers-sub-ready-{int(time.time()*1000)}")
    client.on_message = on_order_ready
    client.connect(BROKER_IP, BROKER_PORT, 10)
    client.subscribe(
        ORDER_READY_TOPIC,
        qos=1
    )
    client.loop_start()
    return client

def mqtt_listen_orders_sent():
    client = create_mqtt_client(f"smartcheers-sub-sent-{int(time.time()*1000)}")
    client.on_message = on_order_sent
    client.connect(BROKER_IP, BROKER_PORT, 10)
    client.subscribe(
        ORDER_SENT_TOPIC,
        qos=1
    )
    client.loop_start()
    return client

def mqtt_publish_train_passing(table_numero):
    """Publie que le train passe par cette table."""
    payload = {"tableNumero": table_numero}
    return mqtt_publish(payload, "smartcheers/train/passing")


def get_formatted_order_for_lora():
    """Retourne les infos de commande formatées pour envoyer au train via LoRa.
    
    Format:
    - client_info: "Prenom NOM"
    - items_str: "produit1:qty1;produit2:qty2;..."
    """
    global current_ready_order
    
    client_info = f"{current_ready_order['client_prenom']} {current_ready_order['client_nom']}"
    
    # Construire la liste des items avec nom et quantité
    items_str = ";".join([
        f"{ligne['produitNom']}:{ligne['quantite']}" 
        for ligne in current_ready_order['lignes']
    ])
    
    return client_info, items_str
