import time
import grovepi

buzzer = 8
grovepi.pinMode(buzzer, "OUTPUT")

def soft_train_horn():
    # impulsions très courtes = volume perçu très bas
    for _ in range(20):
        grovepi.digitalWrite(buzzer, 1)
        time.sleep(0.005)   # ON très court
        grovepi.digitalWrite(buzzer, 0)
        time.sleep(0.08)    # OFF long → son adouci

while True:
    try:
        print("Klaxon très doux 🚆")
        soft_train_horn()
        time.sleep(2)  # grande pause entre klaxons

    except KeyboardInterrupt:
        grovepi.digitalWrite(buzzer, 0)
        break
    except IOError:
        print("Error")

