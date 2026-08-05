"""Publication MQTT sécurisée (TLS + certificats client/serveur) via Paho."""
import ssl
import time
import json
import paho.mqtt.client as paho

from config import BROKER_IP, BROKER_PORT, MQTT_USERNAME, MQTT_PASSWORD

CREATE_ORDER_TOPIC = "smartcheers/orders/new"
ORDER_CREATED_TOPIC = "smartcheers/orders/created"
ORDER_RECEIVED_TOPIC = "smartcheers/orders/received"
ORDER_READY_TOPIC = "smartcheers/orders/ready"
DELIVER_ORDER_TOPIC = "smartcheers/orders/deliver"


CA_CERT = "/home/pi/mqtt-certs/ca.crt"
CLIENT_CERT = "/home/pi/mqtt-certs/client.crt"
CLIENT_KEY = "/home/pi/mqtt-certs/client.key"



def create_mqtt_client(client_id):
    """Création d'un client MQTT sécurisé."""

    client = paho.Client(
        client_id=client_id,
        protocol=paho.MQTTv311
    )

    client.username_pw_set(
        username=MQTT_USERNAME,
        password=MQTT_PASSWORD
    )

    client.tls_set(
        ca_certs=CA_CERT,
        certfile=CLIENT_CERT,
        keyfile=CLIENT_KEY,
        tls_version=ssl.PROTOCOL_TLSv1_2
    )

    return client


def mqtt_publish(payload, mqtt_topic):
    """Publie un message MQTT sécurisé."""

    client = create_mqtt_client("smartcheers-pub-001")

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

        print("✅ Message envoyé")
        return True

    except Exception as e:
        print(f"❌ Erreur MQTT : {e}")
        return False



def on_order_created(client, userdata, msg):
    """Callback appelé lors de la réception d'une commande créée."""

    try:
        payload = json.loads(msg.payload.decode())

        rpi_id = payload.get("rpiId")
        order_id = payload.get("orderId")

        print("📦 Nouvelle commande créée")
        print(f"RPI : {rpi_id}")
        print(f"Order ID : {order_id}")

        # Ici tu peux :
        # - afficher l'ID sur écran
        # - débloquer un état
        # - sauvegarder localement
        # - faire sonner un buzzer

    except Exception as e:
        print(f"❌ Erreur parsing MQTT : {e}")



def mqtt_listen_orders():
    """Écoute permanente des événements MQTT."""

    client = create_mqtt_client("smartcheers-sub-001")

    client.on_message = on_order_created

    try:
        client.connect(BROKER_IP, BROKER_PORT, 10)

        client.subscribe(
            ORDER_CREATED_TOPIC,
            qos=1
        )

        print(f"📡 Écoute MQTT sur {ORDER_CREATED_TOPIC}")

        client.loop_forever()

    except Exception as e:
        print(f"❌ Erreur MQTT listener : {e}")