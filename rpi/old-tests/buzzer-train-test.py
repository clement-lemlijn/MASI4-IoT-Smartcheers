import time
import grovepi

buzzer = 8
grovepi.pinMode(buzzer, "OUTPUT")

def train_horn():
    # montée progressive (son plus doux)
    for i in range(10):
        grovepi.digitalWrite(buzzer, 1)
        time.sleep(0.02)
        grovepi.digitalWrite(buzzer, 0)
        time.sleep(0.03)

    # son maintenu
    for i in range(30):
        grovepi.digitalWrite(buzzer, 1)
        time.sleep(0.03)
        grovepi.digitalWrite(buzzer, 0)
        time.sleep(0.03)

    # descente progressive
    for i in range(10):
        grovepi.digitalWrite(buzzer, 1)
        time.sleep(0.02)
        grovepi.digitalWrite(buzzer, 0)
        time.sleep(0.05)

while True:
    try:
        print("Klaxon de train 🚆")
        train_horn()
        time.sleep(1.5)  # pause entre les coups de klaxon

    except KeyboardInterrupt:
        grovepi.digitalWrite(buzzer, 0)
        break
    except IOError:
        print("Error")

