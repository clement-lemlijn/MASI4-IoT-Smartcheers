import serial

# Connexion au port série du Raspberry Pi
ser = serial.Serial(
    port='/dev/serial0',
    baudrate=9600,
    timeout=1
)

print("🟢 En attente d'un badge RFID...")

while True:
    data = ser.read(14)

    if data:
        try:
            raw = data.decode('ascii', errors='ignore').strip()
            print("📟 Badge détecté :", raw)
        except Exception as e:
            print("Erreur :", e)

