#!/usr/bin/env python3

# actuators/radio.py
import serial
import time
import threading
from mqtt_client import mqtt_publish, RPI_ID, create_mqtt_client, BROKER_IP, BROKER_PORT, get_formatted_order_for_lora
TRAIN_STATUS_TOPIC = "smartcheers/train/status"
TRAIN_CONTROL_TOPIC = "smartcheers/train/control"

PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
MESSAGE = "TRAINSTART"

# Port série partagé (ouvert une seule fois)
_ser = None
_lock = threading.Lock()

debug = False

def _get_serial():
    """Ouvre le port série une seule fois (thread-safe)."""
    global _ser
    with _lock:
        if _ser is None or not _ser.is_open:
            _ser = serial.Serial(
                port=PORT,
                baudrate=BAUDRATE,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=1,
            )
            time.sleep(0.5)  # laisse le module démarrer
        return _ser


def _send(cmd: str):
    """Envoie une commande AT au LA66."""
    ser = _get_serial()
    with _lock:
        ser.write(cmd.encode("ascii"))
        time.sleep(0.3)
        # on vide éventuellement le buffer de réponse
        if ser.in_waiting:
            ser.read_all()


def send_train_loaded(items: dict = None, client_info: str = None):
    """Envoie TRAINLOADED avec les items commandés au train."""
    try:
        try:
            client_info, items_str = get_formatted_order_for_lora()
            print(f"[LoRa] Utilisation des données MQTT : {client_info}")
        except Exception as e:
            print(f"Erreur récupération données MQTT : {e}")
            client_info = "Client"
            items_str = ""

        # On nettoie un peu les données
        client_info = str(client_info).strip().replace("|", " ")
        items_str = str(items_str).strip().replace("|", " ")

        # Nouveau format avec | (beaucoup plus fiable)
        msg = f"TRAINLOADED|{client_info}|{items_str}"

        cmd = f"AT+SEND=1,{msg},0,3\r\n"
        if debug:
            print(f"Envoi TRAINLOADED : {cmd.strip()}")
        _send(cmd)
        print(f"TRAINLOADED envoyé : {msg}")

    except Exception as e:
        print(f"Erreur send_train_loaded : {e}")



def call_train_start():
    """Envoie la commande TRAINSTART au train."""
    try:
        cmd = f"AT+SEND=1,{MESSAGE},0,3\r\n"
        if(debug): print(f"Envoi : {cmd.strip()}")
        _send(cmd)
        print("TRAINSTART envoyé")
    except Exception as e:
        print(f"Erreur call_train_start : {e}")


def send_ack():
    """Envoie KEEPALIVEACK."""
    try:
        ack_msg = "KEEPALIVEACK"
        cmd = f"AT+SEND=1,{ack_msg},0,3\r\n"
        if(debug): print(f"→ ACK envoyé : {ack_msg}")
        _send(cmd)
    except Exception as e:
        print(f"Erreur send_ack : {e}")


def _keepalive_loop():
    """Boucle de réception des messages LoRa (tourne en thread daemon)."""
    print("Keepalive LoRa démarré – en attente de messages...")
    while True:
        try:
            ser = _get_serial()
            if ser.in_waiting > 0:
                data = ser.readline()
                if(debug): print("données reçues:", data)

                if b"Data: (HEX:)" in data:
                    try:
                        start = data.find(b"(HEX:) ") + len(b"(HEX:) ")
                        raw_hex = data[start:].strip()
                        hex_str = raw_hex.decode("utf-8").replace(" ", "")
                        message = bytes.fromhex(hex_str).decode("utf-8", errors="replace")
                        if(debug): print(f"→ Message reçu : {message}")

                        if message.startswith("KEEPALIVE"):
                            if(debug): print(" → Keepalive détecté")
                            send_ack()
                            try:
                                payload = {"rpiId": RPI_ID, "type": "keepalive", "message": message, "ts": int(time.time())}
                                threading.Thread(target=mqtt_publish, args=(payload, TRAIN_STATUS_TOPIC), daemon=True).start()
                            except Exception as e:
                                print(f"Erreur MQTT keepalive : {e}")
                    except Exception as e:
                        print(f"Erreur de parsing : {e}")
        except Exception as e:
            print(f"Erreur keepalive loop : {e}")
            time.sleep(1)


def start_keepalive():
    """Démarre le thread keepalive (à appeler une seule fois au démarrage)."""
    t = threading.Thread(target=_keepalive_loop, daemon=True)
    t.start()


def call_train_stop():
    """Envoie la commande TRAINSTOP au train."""
    try:
        stop_msg = "TRAINSTOP"
        cmd = f"AT+SEND=1,{stop_msg},0,3\r\n"
        if(debug): print(f"Envoi : {cmd.strip()}")
        _send(cmd)
        print("TRAINSTOP envoyé")
    except Exception as e:
        print(f"Erreur call_train_stop : {e}")


def send_train_passed():
    """Envoie le message TRAINPASSED au train pour indiquer qu'il est arrivé à une table."""
    try:
        msg = "TRAINPASSED"
        cmd = f"AT+SEND=1,{msg},0,3\r\n"
        if(debug): print(f"Envoi TRAINPASSED : {cmd.strip()}")
        _send(cmd)
        print("TRAINPASSED envoyé")
    except Exception as e:
        print(f"Erreur send_train_passed : {e}")


def _on_train_control(client, userdata, msg):
    """Handler MQTT pour le topic smartcheers/train/control.

    Attends des payloads simples 'START', 'STOP' ou 'STOPDIST:<val>' (insensible à la casse).
    """
    try:
        payload = msg.payload.decode("utf-8", errors="ignore").strip().upper()
        if debug: print(f"MQTT control reçu : {payload}")
        if payload == "START":
            if debug: print("→ Envoi TRAINSTART via LoRa (contrôle MQTT)")
            call_train_start()
        elif payload == "STOP":
            if debug: print("→ Envoi TRAINSTOP via LoRa (contrôle MQTT)")
            call_train_stop()
        elif payload.startswith("STOPDIST:"):
            try:
                val_str = payload.split(":", 1)[1].strip()
                dist = int(val_str)
                # clamp between 3 and 100 cm
                dist = max(3, min(100, dist))
                cmd_msg = f"STOPDIST:{dist}"
                cmd = f"AT+SEND=1,{cmd_msg},0,3\r\n"
                if debug: print(f"→ Envoi STOPDIST via LoRa : {cmd_msg}")
                _send(cmd)
                print(f"STOPDIST {dist} envoyé")
            except Exception as e:
                print(f"Erreur parsing STOPDIST : {e}")
        else:
            print(f"Payload inconnu sur {TRAIN_CONTROL_TOPIC} : {payload}")
    except Exception as e:
        print(f"Erreur gestion control MQTT : {e}")


def start_train_control_listener():
    """Démarre un client MQTT en fond pour écouter les commandes START/STOP.

    Retourne le client paho (permet de l'arrêter plus tard si besoin).
    """
    try:
        client = create_mqtt_client(f"smartcheers-sub-trainctl-{int(time.time()*1000)}")
        client.on_message = _on_train_control
        client.connect(BROKER_IP, BROKER_PORT, 10)
        client.subscribe(TRAIN_CONTROL_TOPIC, qos=1)
        client.loop_start()
        print(f"Écoute control train sur {TRAIN_CONTROL_TOPIC} démarrée")
        return client
    except Exception as e:
        print(f"Erreur démarrage listener control MQTT : {e}")
        return None


def close():
    """Ferme proprement le port série."""
    global _ser
    with _lock:
        if _ser is not None and _ser.is_open:
            _ser.close()
            _ser = None