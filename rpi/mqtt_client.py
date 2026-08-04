"""Publication MQTT sécurisée (TLS + certificats client/serveur) via Paho."""
import ssl
import time
import paho.mqtt.client as paho

from config import BROKER_IP, BROKER_PORT, MQTT_USERNAME, MQTT_PASSWORD

CREATE_ORDER_TOPIC = "smartcheers/orders/new"
DELIVER_ORDER_TOPIC = "smartcheers/orders/deliver"


def mqtt_publish(payload, mqtt_topic):
    """Publie un message MQTT sécurisé. Retourne True/False, ne gère aucun affichage."""
    client = paho.Client(client_id="smartcheers-pub-001", protocol=paho.MQTTv311)
    client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
    client.tls_set(
        ca_certs="/home/pi/mqtt-certs/ca.crt",
        certfile="/home/pi/mqtt-certs/client.crt",
        keyfile="/home/pi/mqtt-certs/client.key",
        tls_version=ssl.PROTOCOL_TLSv1_2
    )

    try:
        # Timeout réduit pour éviter de bloquer le script trop longtemps
        client.connect(BROKER_IP, BROKER_PORT, 10)
        client.loop_start()
        client.publish(mqtt_topic, payload, 0)
        time.sleep(1)
        client.loop_stop()
        client.disconnect()
        print("✅ Message envoyé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur MQTT : {e}")
        return False