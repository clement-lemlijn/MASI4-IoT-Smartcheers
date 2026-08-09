"""SmartCheers - RPi : point d'entrée. Gère le menu, le panier et le cycle de commande."""
import time
import json
import RPi.GPIO as GPIO
from grove_rgb_lcd import setText
import threading

from config import RPI_ID, DRINKS, SNACKS, BROKER_IP, BROKER_PORT
from mqtt_client import mqtt_publish, create_mqtt_client, CREATE_ORDER_TOPIC, mqtt_listen_orders_creation, order_received, mqtt_listen_orders_ready, order_ready, received_order_id, mqtt_listen_orders_preparation, mqtt_listen_orders_sent, order_preparation, order_sent, mqtt_publish_train_passing
from leds import setup_leds, set_leds, blink_led
from display import safe_setRGB, init_lcd, display_menu, display_panier, display_order_status
from joystick import setup_joystick, read_joystick, X_LEFT, X_RIGHT, Y_UP, Y_DOWN
from rfid import wait_for_rfid
from activity import touch_activity, is_timed_out
from actuators.servos import open_bifurcation, close_bifurcation, open_barrier, close_barrier
from actuators.rpiLoRa import call_train_start, start_keepalive, start_train_control_listener, close, send_train_loaded, send_train_passed
from sensors.light_sensor import wait_for_train
from camera_api import start_camera_server

MAIN_MENU = ["Boissons", "Snacks", "Confirmer", "Annuler"]

# Info reçu du serveur après handshake MQTT au démarrage
CONNECT_INFO = None


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

                # Réinitialiser les Events avant d’écouter
                order_received.clear()
                order_preparation.clear()
                order_ready.clear()
                order_sent.clear()
                received_order_id = None

                # 1. Écoute de tous les statuts en parallèle
                mqtt_client_created = mqtt_listen_orders_creation()
                mqtt_client_prep = mqtt_listen_orders_preparation()
                mqtt_client_ready = mqtt_listen_orders_ready()
                mqtt_client_sent = mqtt_listen_orders_sent()

                print("Attente confirmation serveur...")
                is_order_received = order_received.wait(timeout=10)

                if is_order_received:
                    print("Commande reçue !")
                    display_order_status("received")
                    time.sleep(2)

                    # Attendre la préparation
                    print("Attente en préparation...")
                    is_order_prep = order_preparation.wait(timeout=600)
                    if is_order_prep:
                        display_order_status("preparation")
                        time.sleep(1)
                    
                    # Attendre que la commande soit prête
                    print("Attente commande prête...")
                    is_order_ready = order_ready.wait(timeout=600)

                    if is_order_ready:
                        display_order_status("ready")
                        time.sleep(1)

                        # Envoyer TRAINLOADED avec les données MQTT de commande prête
                        send_train_loaded()
                        time.sleep(1)

                        # Attendre l'envoi par le train
                        print("Attente envoi par train...")
                        is_order_sent = order_sent.wait(timeout=60)
                        if is_order_sent:
                            display_order_status("sent")
                            time.sleep(1)

                        # Make sure the table 2 "STOP" barrier is closed
                        close_barrier()

                        # Open the table 2 bifurcation
                        open_bifurcation()
                        time.sleep(2)
                        print("bifurcation openned")

                        # Faire démarrer le train automatiquement
                        call_train_start()

                        # Attendre le train
                        wait_for_train()

                        # Envoyer TRAINPASSED au train via LoRa
                        # send_train_passed()
                        # time.sleep(1)

                        close_bifurcation()
                        time.sleep(2)
                        print("bifurcation closed")
                    else:
                        print("Commande trop lente")
                        setText("Commande trop lente")
                        safe_setRGB(255, 0, 0)
                        blink_led("red", times=2)

                    # Arrêter tous les clients MQTT
                    mqtt_client_created.loop_stop()
                    mqtt_client_created.disconnect()
                    mqtt_client_prep.loop_stop()
                    mqtt_client_prep.disconnect()
                    mqtt_client_ready.loop_stop()
                    mqtt_client_ready.disconnect()
                    mqtt_client_sent.loop_stop()
                    mqtt_client_sent.disconnect()
                else:
                    print("Pas de confirmation serveur")
                    setText("Serveur absent")
                    safe_setRGB(255, 0, 0)
                    blink_led("red", times=2)
                    mqtt_client_created.loop_stop()
                    mqtt_client_created.disconnect()
                    mqtt_client_prep.loop_stop()
                    mqtt_client_prep.disconnect()
                    mqtt_client_ready.loop_stop()
                    mqtt_client_ready.disconnect()
                    mqtt_client_sent.loop_stop()
                    mqtt_client_sent.disconnect()

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
    # Default: light red
    safe_setRGB(255, 100, 100)
    setText("Connexion...")
    set_leds()

    #####################################################
    ################ CONNECT TO BAR #####################
    #####################################################

    # Startup MQTT handshake: publish rpiId and wait for server response
    try:
        print("🔌 Publishing connect message...")
        mqtt_publish({"rpiId": RPI_ID}, "smartcheers/rpi/connect")
        # Listen for success response on smartcheers/rpi/connect/success
        client_hs = create_mqtt_client(f"smartcheers-hs-sub-{int(time.time()*1000)}")
        handshake_event = threading.Event()
        def on_connect_success(client, userdata, msg):
            global CONNECT_INFO
            try:
                payload = json.loads(msg.payload.decode())
                if payload.get("rpiId") != RPI_ID:
                    return
                CONNECT_INFO = payload
                print("✅ Connect success received:", CONNECT_INFO)
                handshake_event.set()
            except Exception as e:
                print("Erreur handshake MQTT:", e)
        client_hs.on_message = on_connect_success
        client_hs.connect(BROKER_IP, BROKER_PORT, 10)
        client_hs.subscribe("smartcheers/rpi/connect/success", qos=1)
        client_hs.loop_start()
        print("Attente réponse serveur sur smartcheers/rpi/connect/success...")
        got = handshake_event.wait(timeout=30)
        client_hs.loop_stop()
        client_hs.disconnect()
        if not got:
            print("⚠️ Pas de réponse serveur pour le handshake (timeout).")
            setText("Serveur absent")
            safe_setRGB(255, 0, 0)
            return
        else:
            # Connection successful: green for 2 seconds
            safe_setRGB(0, 255, 0)
            setText("Connecte !")
            time.sleep(2)
            # Now switch to light blue for normal operation
            safe_setRGB(100, 150, 255)
            setText("Pret")
            time.sleep(0.5)
    except Exception as e:
        print("Erreur handshake:", e)



    # Démarrer le serveur Flask pour la caméra dans un thread daemon
    camera_token = CONNECT_INFO.get("activeVisit", {}).get("token") if CONNECT_INFO else None
    print("camera_token:", camera_token)
    camera_thread = threading.Thread(
        target=start_camera_server, 
        args=(camera_token,), 
        daemon=True
    )
    camera_thread.start()
    print("📷 Serveur caméra lancé sur http://0.0.0.0:5000")
    time.sleep(2)  # Laisser le temps au serveur de démarrer

    start_keepalive()

    # TEMP
    open_bifurcation()

    open_barrier() # test
    time.sleep(2)

    # Closing table2's "STOP" barrier
    print("closing barrier")
    close_barrier()

    # Closing bifurcation
    print("closing bifurcation")
    close_bifurcation()

    # Listener MQTT pour commandes START/STOP du train
    start_train_control_listener()

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
        close() # close port série d'écoute LoRa
        GPIO.cleanup()