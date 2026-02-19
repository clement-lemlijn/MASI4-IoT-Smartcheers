
import network
sta=network.WLAN(network.STA_IF)
if not sta.isconnected():
    print('Connexion au WiFi')
    sta.active(True)
    sta.ifconfig(('192.168.137.21', '255.255.255.0', '192.168.1.1', '8.8.8.8'))
    sta.connect('OMEN-CLEMENT 9147','clement123')
    while not sta.isconnected():
        pass
    print('Connected ! Config : ', sta.ifconfig())

import sendMQTT
