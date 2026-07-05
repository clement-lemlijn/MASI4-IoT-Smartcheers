# 🍻 SmartCheers – RaspberryPI

<img src="https://m.media-amazon.com/images/I/71Yjs1JDM-S._AC_UF1000,1000_QL80_.jpg" alt="Photo Rpi" width="400" style="display: block; margin-left: auto; margin-right: auto;"/>

## Hardware & OS
Le Raspberry Pi est configuré sur une base système spécifique :
- **Operating System :** Raspbian GNU/Linux 10 (buster)
- **Kernel :** Linux 5.10.17-v7l+
- **Architecture :** arm (armv7l)

## Connexion

Le Raspberry PI a une ip statique `192.168.137.83`. Ses paramètres WiFi sont définis sur : (Hostspot de mon ordinateur)
Pour s'y connecter, entrer dans un invite de commande : 
```
ssh pi@192.168.137.83
```
Password : `hepl`

### WiFi
Il est connecté au hostpot windows selon les paramètres suivants : 
```conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=BE
network={
ssid="OMEN-CLEMENT 9147"
psk="clement123"
key_mgmt=WPA-PSK
}
```


### Ethernet
On peut également s'y connecter en ethernet, son ip actuelle est `192.168.68.70`
```
ssh pi@192.168.68.70
```

```
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether dc:a6:32:31:98:98 brd ff:ff:ff:ff:ff:ff
    inet 192.168.68.70/22 brd 192.168.71.255 scope global dynamic noprefixroute eth0
       valid_lft 7162sec preferred_lft 6262sec
    inet6 fe80::68d8:270a:28fa:ff8f/64 scope link
       valid_lft forever preferred_lft forever
```
_`ip -c addr show eth0`_

## Structure

```
smartcheers/
└── rpi/
    ├── smart_cheers_menu.py    # Script principal de l'application
    └── test/                   # Scripts de test pour le projet
```

## Service 🔧

### Github runner :
```
sudo systemctl status actions.runner.clement-lemlijn-MASI4-IoT-Smartcheers.raspberrypi.service
```
### Smartcheers menu :
```
systemctl status smartcheers.service
```

## Avant de débrancher :
```
sudo shutdown now
```
