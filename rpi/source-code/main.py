"""SmartCheers - RPi : point d'entrée. Gère le menu, le panier et le cycle de commande."""
import time
import json
import RPi.GPIO as GPIO
from grove_rgb_lcd import setText

from config import RPI_ID, DRINKS, SNACKS
from mqtt_client import mqtt_publish, CREATE_ORDER_TOPIC, mqtt_listen_orders
from leds import setup_leds, set_leds, blink_led
from display import safe_setRGB, init_lcd, display_menu, display_panier
from joystick import setup_joystick, read_joystick, X_LEFT, X_RIGHT, Y_UP, Y_DOWN
from rfid import wait_for_rfid
from activity import touch_activity, is_timed_out

MAIN_MENU = ["Boissons", "Snacks", "Confirmer", "Annuler"]


def annuler_commande(raison="Commande annulee"):
    """Reset visuel/LED lors d'une annulation (manuelle ou par timeout)."""
    safe_setRGB(255, 0, 0)
    blink_led("red", times=3, delay=0.2)
    setText(raison)
    time.sleep(2)


def _handle_confirmation(client_id, panier, menu_stack, index):
    """Gère l'écran de confirmation de commande.

    Retourne True si la session (commande) doit se terminer, False si on
    reste dans la même session (retour au menu ou échec MQTT à retenter).
    """
    if not panier:
        safe_setRGB(255, 0, 0)
        blink_led("red", times=2, delay=0.2)
        setText("Panier vide !")
        time.sleep(2)
        return True

    safe_setRGB(255, 255, 0)
    setText("Confirmer ?\n")
    display_panier(panier)
    time.sleep(0.5)

    while True:
        if is_timed_out():
            annuler_commande("Session expiree\nCommande annulee")
            return True

        x_c, y_c, sw_c = read_joystick()

        if sw_c == 0:
            touch_activity()
            payload = json.dumps({
                "rpiId": RPI_ID,
                "badgeUid": client_id,
                "command": [
                    {"produitId": produit_id, "quantite": quantite}
                    for produit_id, quantite in panier.items()
                ]
            })
            success = mqtt_publish(payload, CREATE_ORDER_TOPIC)

            if success:
                print("Commande envoyée avec succès")
                safe_setRGB(0, 255, 0)
                set_leds(green=True)
                setText("Commande envoyee")
                time.sleep(2)

                # démarre écoute MQTT
                mqtt_client = mqtt_listen_orders()
                print("Attente confirmation serveur...")
                received = order_received.wait(timeout=10) # attente max 10 secondes

                if received:
                    print("Commande reçue !")
                    setText("Commande recue")
                    time.sleep(2)
                else:
                    print("Pas de confirmation serveur")
                    setText("Serveur absent")
                    safe_setRGB(255, 0, 0)
                    blink_led("red", times=2)

                mqtt_client.loop_stop()
                mqtt_client.disconnect()
                set_leds()
                return True
            else:
                print("Échec MQTT : Impossible d'envoyer la commande")
                safe_setRGB(255, 0, 0)
                blink_led("red", times=2, delay=0.2)
                setText("Erreur Serveur !")
                time.sleep(2)
                return False  # on annule la progression, la commande reste ouverte

        elif x_c < X_LEFT:
            touch_activity()
            display_menu(menu_stack[-1], index, panier)
            return False  # retour au menu, session conservée

        time.sleep(0.05)


def run():
    setup_joystick()
    setup_leds()
    init_lcd()
    set_leds()

    while True:
        client_id = wait_for_rfid()
        touch_activity()
        index = 0
        menu_stack = [MAIN_MENU]
        panier = {}
        show_panier = False
        display_menu(menu_stack[-1], index, panier)

        commande_terminee = False
        while not commande_terminee:

            # --- Vérification du timeout d'inactivité ---
            if is_timed_out():
                print("⏱️ Timeout d'inactivité, annulation de la session")
                annuler_commande("Session expiree\nCommande annulee")
                break

            x, y, sw = read_joystick()

            # Bascule écran menu / panier
            if x > X_RIGHT:
                touch_activity()
                show_panier = True
                display_panier(panier)
                time.sleep(0.3)
            elif x < X_LEFT:
                touch_activity()
                show_panier = False
                display_menu(menu_stack[-1], index, panier)
                time.sleep(0.3)

            if not show_panier:
                # Navigation BAS
                if y > Y_DOWN:
                    touch_activity()
                    index = (index + 1) % len(menu_stack[-1])
                    display_menu(menu_stack[-1], index, panier)
                    time.sleep(0.3)

                # Navigation HAUT
                elif y < Y_UP:
                    touch_activity()
                    index = (index - 1) % len(menu_stack[-1])
                    display_menu(menu_stack[-1], index, panier)
                    time.sleep(0.3)

                # RETOUR
                elif x < X_LEFT and len(menu_stack) > 1:
                    touch_activity()
                    menu_stack.pop()
                    index = 0
                    display_menu(menu_stack[-1], index, panier)
                    time.sleep(0.3)

                # VALIDATION
                elif sw == 0:
                    touch_activity()
                    choice = menu_stack[-1][index]

                    if choice == "Boissons":
                        menu_stack.append(DRINKS)
                        index = 0
                        display_menu(DRINKS, index, panier)

                    elif choice == "Snacks":
                        menu_stack.append(SNACKS)
                        index = 0
                        display_menu(SNACKS, index, panier)

                    elif choice == "Annuler":
                        annuler_commande("Commande annulee\npar l'utilisateur")
                        commande_terminee = True

                    elif choice == "Confirmer":
                        commande_terminee = _handle_confirmation(
                            client_id, panier, menu_stack, index
                        )

                    else:
                        produit_id = choice["id"]
                        panier[produit_id] = panier.get(produit_id, 0) + 1
                        display_menu(menu_stack[-1], index, panier)

                    time.sleep(0.3)

            time.sleep(0.05)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        setText("Arrêt")
        safe_setRGB(255, 0, 0)
        set_leds()
    finally:
        GPIO.cleanup()