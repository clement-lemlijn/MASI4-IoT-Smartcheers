import paho.mqtt.client as paho
import time

broker_ip = "192.168.68.77"
broker_port = 1883
mqtt_topic = "smartcheers/order/create"
payload = 'Commande envoyée : {"clientUid": "\u000227004228D09D\u0003", "command": [{"produit": "Coca", "quantite": 2}]}'

def on_connect(clientf, userdata, flags, rc):
    print("Connected with result code", rc)
    client.publish(mqtt_topic, payload)

def on_publish(client, userdata, mid):
    print("Message published")

def mqtt_publish(payload):
    client = paho.Client()
    client.username_pw_set(username='clement',password='heplhepl')
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker_ip, broker_port, 60)
    client.loop_start()
    time.sleep(2)
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    mqtt_publish(payload)
