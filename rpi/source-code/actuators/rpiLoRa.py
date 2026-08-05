#!/usr/bin/env python3

# actuators/radio.py

import serial
import time

PORT = "/dev/ttyUSB0"
BAUDRATE = 9600

MESSAGE = "TRAINSTART"

def call_train(message):
    try:
        ser = serial.Serial(
            PORT,
            BAUDRATE,
            timeout=2
        )

        time.sleep(1)  # laisse le module démarrer

        # Commande LA66 :
        # AT+SEND=<port>,<payload>,<ack>,<length> non tu es con GEMINI !!!
        cmd = f"AT+SEND=1,{message},0,{3}\r\n"

        print(f"Envoi : {cmd.strip()}")

        ser.write(cmd.encode("ascii"))

        # Lire la réponse du LA66
        time.sleep(0.5)

        response = ser.read_all().decode(errors="ignore")

        print("Réponse LA66 :")
        print(response)

        ser.close()

    except Exception as e:
        print(f"Erreur : {e}")
