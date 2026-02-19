import time
import grovepi

# Temperature & Humidity Sensor v1.2
# Branché sur le port digital D2
sensor = 2      # D2
blue = 0        # 0 = capteur bleu (v1.2)

while True:
    try:
        temp, humidity = grovepi.dht(sensor, blue)

        if temp is not None and humidity is not None:
            print(f"Température = {temp:.1f} °C")
            print(f"Humidité   = {humidity:.1f} %")
        else:
            print("Lecture invalide")

        time.sleep(1)

    except KeyboardInterrupt:
        break
    except IOError:
        print("Erreur I2C")
