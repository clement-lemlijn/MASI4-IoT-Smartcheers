import paho.mqtt.client as paho
import time

# --- CONFIGURATION ---
broker_ip = "192.168.137.1" 
broker_port = 8884
mqtt_topic = "smartcheers/order/create"
ca_cert_path = "/home/pi/mqtt-certs/ca.crt" # Ton certificat existant
user = "clement-lemlijn"
password = "mqtt-pwd"
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
    client.username_pw_set(username=user, password=password)

    # Activation du TLS
    client.tls_set(ca_certs=ca_cert_path)

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
