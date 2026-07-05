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
