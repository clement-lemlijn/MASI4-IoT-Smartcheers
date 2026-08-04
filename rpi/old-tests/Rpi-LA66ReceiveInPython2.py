import serial
import re

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    timeout=1
)

hex_pattern = re.compile(rb'Data: \(HEX:\)\s*(.*)')

while True:
    line = ser.readline()
    if not line:
        continue

    print("brut :", line)

    match = hex_pattern.search(line)
    if match:
        hex_data = match.group(1).strip()
        try:
            # convertir "48 65 6c..." -> bytes -> string
            decoded = bytes.fromhex(hex_data.decode()).decode('utf-8')
            print("📦 message décodé :", decoded)
        except Exception as e:
            print("Erreur décodage :", e)
