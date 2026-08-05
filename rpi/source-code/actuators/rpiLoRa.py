#!/usr/bin/env python3

# actuators/radio.py
import serial
import time
import threading

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
                    except Exception as e:
                        print(f"Erreur de parsing : {e}")
        except Exception as e:
            print(f"Erreur keepalive loop : {e}")
            time.sleep(1)


def start_keepalive():
    """Démarre le thread keepalive (à appeler une seule fois au démarrage)."""
    t = threading.Thread(target=_keepalive_loop, daemon=True)
    t.start()


def close():
    """Ferme proprement le port série."""
    global _ser
    with _lock:
        if _ser is not None and _ser.is_open:
            _ser.close()
            _ser = None