# 🍻 SmartCheers – Node-RED (VM Ubuntu)

<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrdWsJtbpe2vnrDm67btUVWifMLzek0QVWGap-Mjyz-w&s=10" alt="Logo Node-RED" width="200" style="display: block; margin-left: auto; margin-right: auto;"/>

## Description
Le conteneur Node-RED sert de centre névralgique pour la logique métier et l'interface utilisateur (Dashboard) de SmartCheers. Il communique avec le Raspberry Pi via le broker MQTT pour piloter le train électrique.

## Installation & Configuration Docker
L'infrastructure est déployée via Docker pour garantir la portabilité et le redémarrage automatique.

### Structure du projet
Le projet est organisé comme suit :
```text
~/docker/node-red/
├── docker-compose.yml
└── data/           # Volumes persistants (flows, config)
```

## Service

```
sudo docker compose ps
sudo docker compose logs -f
sudo docker stats
```

Accès interface : [http://192.168.1.12:1880/ui](http://192.168.1.12:1880/ui)
