# 🍻 SmartCheers – Tp-Link Nano router

<img src="../assets/tp-link_nano-router.png" alt="Tp Link nano router" width="400" style="display: block; margin-left: auto; margin-right: auto;"/>

## Connection
**SSID:** `TP-Link_3384`

**Pwd:** `50165391`

### Configuration interface 
<img src="../assets/tp-link_nano-router_config-interface.png" alt="Tp Link nano router" width="400" style="display: block; margin-left: auto; margin-right: auto;"/>

Address: http://192.168.1.1/

User: admin

Pwd: admin


Debug afficher les réseaux détectés par le rpi `sudo iwlist wlan0 scan | grep ESSID`
```
# More debug
journalctl -f -u wpa_supplicant
sudo wpa_supplicant -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf -d
```
