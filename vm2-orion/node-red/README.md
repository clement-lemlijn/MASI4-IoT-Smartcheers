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

Accès interface depuis vm : [http://127.0.0.1:1880/](http://127.0.0.1:1880/)

Accès interface depuis pc : [http://192.168.1.12:1880/](http://192.168.1.12:1880/)


## Palettes installées
Voici les palettes installées sur ma session node-red :
- `node-red-dashboard`
- `node-red-node-mongodb`


### Définir les bons droits après installation 

```
sudo chown -R $USER:$USER ./data
sudo chmod -R 775 ./data
```

utilisateur node-red UID 1000.
```
sudo chown -R 1000:1000 client_data employee_data
```
