import time
import grovepi

# Port analogique utilisé
JOYSTICK_X = 0

print("Lecture de l'axe X du joystick (CTRL+C pour quitter)")

while True:
    try:
        x_value = grovepi.analogRead(JOYSTICK_X)
        print("Axe X :", x_value)
        time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nArrêt du script")
        break
    except IOError:
        print("Erreur de lecture")
        time.sleep(0.5)

