import time
import grovepi
import json
import serial

# -----------------------------
# GROVE DHT
# -----------------------------
sensor = 2
blue = 0

# -----------------------------
# USB SERIAL (LoRa Adapter)
# -----------------------------
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)

print("USB → LoRa prêt")

# -----------------------------
# LOOP
# -----------------------------
try:
    while True:
        temp, hum = grovepi.dht(sensor, blue)

        if temp is not None and hum is not None:
            data = {
                "t": round(temp, 1),
                "h": round(hum, 1)
            }

            payload = json.dumps(data)

            print("TX USB:", payload)
            ser.write((payload + "\n").encode())

        else:
            print("Lecture capteur invalide")

        time.sleep(10)

except KeyboardInterrupt:
    print("Arrêt")

finally:
    ser.close()
