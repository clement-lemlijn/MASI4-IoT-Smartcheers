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

Accès interface depuis pc (https - client) : [https://192.168.1.12:1880/](https://192.168.1.12:1880/)

Accès interface depuis pc (https - employee) : [https://192.168.1.12:1881/](https://192.168.1.12:1881/)



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

pour activer l'authentification : ex employee_data/setting.js/"adminAuth: {.."
pour générer un mot de passe : `sudo docker exec -it node-red-employee node-red admin hash-pw` 

"httpNodeAuth: [.. " pour bloquer /ui


## Instances Node-RED

Deux instances Node-RED distinctes tournent en parallèle, chacune avec son propre rôle, ses propres flows et sa propre authentification :

| Instance | Rôle | Port | Volume `/data` | Certificat TLS |
|---|---|---|---|---|
| `node-red-client` | Interface client final (niveau 2) | `1880` | `./client_data` & `config/certs` | `node-red.crt` / `.key` |
| `node-red-employee` | Interface employé / entreprise (niveau 2) | `1881` | `./employee_data` & `config/certs/employee` | `node-red-employee.crt` / `.key` |

les certificats sont générés grâce aux scripts `MASI4-IoT-Smartcheers/vm2-orion/mqtt-broker
/scripts/generate-node-red-certs.sh` & `MASI4-IoT-Smartcheers/vm2-orion/mqtt-broker
/scripts/generate-node-red-employee-certs.sh`

Chaque instance possède son propre mot de passe (`adminAuth`/`httpNodeAuth`) **et** son propre certificat TLS, afin qu'une compromission éventuelle d'une clé n'impacte pas l'autre instance.

## Certificats HTTPS

Les certificats sont stockés sur la VM dans :
`~/MASI4-IoT-Smartcheers/vm2-orion/mqtt-broker/config/certs/`

et montés dans chaque conteneur via un bind mount Docker :
```yaml
volumes:
  - ../mqtt-broker/config/certs:/certs
```

Dans chaque `settings.js` correspondant :
```js
https: {
    key: require("fs").readFileSync('/certs/node-red-employee.key'),
    cert: require("fs").readFileSync('/certs/node-red-employee.crt')
},
requireHttps: true,
```

### Droits sur les certificats
commandes : 
```
sudo chown -R 1000:1000 ./config/certs
sudo chmod 755 ./config/certs
sudo chmod 644 ./config/certs/ca.crt
sudo chmod 644 ./config/certs/node-red.crt
sudo chmod 600 ./config/certs/node-red.key
```

### Confiance navigateur
Les certificats sont auto-signés (CA interne `ca.crt`). Pour éviter l'avertissement "site dangereux", il faudrait importer `ca.crt` dans le magasin de certificats de confiance du navigateur utilisé.


## Mongodb 
`mongosh "mongodb://admin:[admin-pwd]@localhost:27017/admin"`
`mongosh "mongosh "mongodb://nodered:[pwd]@localhost:27017/smartpub_db?authSource=smartpub_db""`

