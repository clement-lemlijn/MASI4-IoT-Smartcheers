# Claude
| # | Vulnérabilité OWASP IoT | Mesures mises en place dans Smartcheers |
|---|---|---|
| 1 | Weak, Guessable, or Hardcoded Passwords | Comptes MQTT distincts par client/employé (pas de mot de passe partagé), authentification `nodered_app` dédiée avec droits minimaux sur MongoDB, tokens de visite uniques (`/dashboard?t=<token>`) remplaçant l'ancien système de mot de passe partagé, `VISIT_ID` par token dans `config.json` pour l'API caméra du RPi. |
| 2 | Insecure Network Services | Mosquitto exposé sur 3 listeners distincts (1883 non chiffré, 8883 TLS, 8884 mTLS obligatoire) avec ACL par client via substitution `%u`, MongoDB bindé sur `127.0.0.1` uniquement (pas exposé au réseau), séparation des VMs Orion (infra bar) / Artemis (infra société) limitant la surface d'attaque, architecture réseau locale/NAT documentée comme argument de défense (vérifié via Shodan/InternetDB). |
| 3 | Insecure Ecosystem Interfaces | `adminAuth` + `httpNodeAuth` sur Node-RED, HTTPS avec certificats auto-signés (bind mounts) sur les dashboards, API Flask du RPi protégée par token d'authentification, séparation stricte des interfaces client (dashboard par token, lecture seule) vs employé (Node-RED 1880/1881) vs télémaintenance (Webex bot, Node-RED 1882). |
| 4 | Lack of Secure Update Mechanisms | *(point le plus faible du projet)* — pas de mécanisme de mise à jour OTA sécurisé pour les firmwares ESP32-H2 actuellement ; déploiement RPi via `systemd` avec code versionné en dépôt Git, ce qui permet une traçabilité des changements mais pas un vrai pipeline de mise à jour signée/anti-rollback — point à documenter comme limite connue dans le rapport. |
| 5 | Use of Insecure or Outdated Components | Stack applicative modulaire et maintenue (Python/Flask, Node-RED, MongoDB via Docker avec image officielle), utilisation de bibliothèques standards (Paho MQTT, GrovePi) plutôt que composants tiers obscurs, choix conscient de la stack legacy caméra (`raspistill`/`raspivid`) documenté et justifié plutôt que subi. |
| 6 | Insufficient Privacy Protection | Séparation des données BADGE/CLIENT/VISITE (minimisation), `commandes` ne référence que `visiteId` (pas d'exposition directe de données client), dashboard client isolé par token à durée de visite limitée (pas d'accès permanent aux données), schéma de validation strict MongoDB empêchant l'injection de données non conformes. |
| 7 | Insecure Data Transfer and Storage | TLS/mTLS sur MQTT (8883/8884), HTTPS sur Node-RED, authentification MongoDB via `authSource=smartpub_db` avec utilisateur dédié `nodered_app`, communications Thread chiffrées nativement (OpenThread), UART local entre modules RPi (surface d'attaque physique réduite). |
| 8 | Lack of Device Management | Registre structuré des devices en base (`raspberrypi`, `tables`, `badges`), monitoring/télémaintenance centralisée sur VM Artemis (`telemaintenance_events`, alertes Webex par bar), déploiement RPi géré via `systemd` (pas de gestion manuelle ad hoc), architecture C4 documentant l'inventaire complet des composants. |
| 9 | Insecure Default Settings | Aucune configuration par défaut partagée : chaque client/table/employé a ses propres identifiants MQTT générés, ACL par utilisateur (`%u`) empêchant l'accès croisé, pas de mot de passe MongoDB par défaut (utilisateur `nodered_app` créé explicitement via script d'init Docker). |
| 10 | Lack of Physical Hardening | Point plus faible côté ESP32-H2/RPi (pas de secure boot documenté, ports de debug UART/GPIO accessibles physiquement) — argument développé dans le rapport : risque atténué par le fait que les devices sont en environnement contrôlé (bar), mais reconnu comme axe d'amélioration plutôt que mesure réellement implémentée. |

# Gemini
| OWASP IoT Vulnerability | Implémentation dans Smartcheers (ESP32 LoRa) |
| :--- | :--- |
| **1. Weak, Guessable, or Hardcoded Passwords** | Absence d'interface web d'administration avec des identifiants par défaut ; utilisation d'une identification par ID de nœud LoRa. |
| **2. Insecure Network Services** | Utilisation d'un réseau radio LoRa privé et fermé ; désactivation de tout service réseau externe ou port d'écoute inutile sur l'ESP32. |
| **3. Insecure Ecosystem Interfaces** | Sécurisation de la liaison avec la passerelle (Raspberry Pi / module LA66 via liaison série) et validation stricte des trames reçues. |
| **4. Lack of Secure Update Mechanisms** | Mises à jour du microcontrôleur effectuées physiquement via liaison USB sécurisée lors des phases de déploiement local. |
| **5. Use of Insecure or Outdated Components** | Utilisation des versions récentes et stables du core Arduino ESP32 et des bibliothèques de capteurs maintenues. |
| **6. Insufficient Privacy Protection** | Aucune collecte de données personnelles ; transmission exclusive de données techniques et de télémétrie (distances ultrasons, état du train). |
| **7. Insecure Data Transfer and Storage** | Absence de stockage de données sensibles sur la mémoire flash de l'ESP32 ; traitement volatile des informations de capteurs. |
| **8. Lack of Device Management** | Suivi de l'état des appareils et des messages via les identifiants uniques LoRa et les logs de débogage série. |
| **9. Insecure Default Settings** | Désactivation des modes de débogage verbeux et configuration explicite des paramètres matériels au démarrage du firmware. |
| **10. Lack of Physical Hardening** | Intégration de l'ESP32 Heltec et des capteurs dans un boîtier physique dédié (projet train Lego) pour protéger l'électronique embarquée. |

# Chatgpt
| # | Vulnérabilité OWASP IoT | Ce qui a été mis en place dans Smart Cheers |
|---|---|---|
| **1** | **Weak, Guessable, or Hardcoded Passwords** | Les identifiants sensibles ne sont pas directement écrits dans le code. Pour MongoDB, le nom d’utilisateur et le mot de passe sont fournis via des **variables d’environnement** (`MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`) et un fichier `.env`. Node-RED utilise également une authentification pour son interface employé, avec des comptes distincts (`admin`, `julie`, `florian`). |
| **2** | **Insecure Network Services** | Les communications IoT reposent principalement sur **MQTT**, avec une configuration permettant l'utilisation de **MQTT over TLS sur le port 8883**. Le serveur Node-RED est séparé du Raspberry Pi et les services sont répartis entre les différentes machines/VM. Les ports inutiles ne sont pas exposés publiquement. |
| **3** | **Insecure Ecosystem Interfaces** | Les interfaces Node-RED sont protégées par **authentification** pour le portail employé. Les dashboards destinés aux tables utilisent également un **token propre à chaque table** (`/dashboard?t=<token>`), afin d'éviter qu'une table puisse simplement accéder au dashboard d'une autre. Les API et flux MQTT sont séparés selon leur fonction (`orders/new`, `orders/preparation`, etc.). |
| **4** | **Lack of Secure Update Mechanisms** | Le projet utilise des composants logiciels provenant de dépôts et images connus (Python, Node-RED, MongoDB Docker, bibliothèques Grove, etc.) et les composants peuvent être mis à jour indépendamment. Cependant, **aucun mécanisme OTA sécurisé complet avec signature, validation du firmware et anti-rollback n'a été implémenté** pour les Raspberry Pi/ESP32. Cette vulnérabilité est donc seulement partiellement couverte. |
| **5** | **Use of Insecure or Outdated Components** | Les dépendances sont basées sur des composants connus : **Docker pour MongoDB**, Node.js/Node-RED, Python et bibliothèques matérielles. Les versions utilisées sont identifiées dans l'environnement de développement. La conteneurisation de MongoDB permet également d'isoler le service de la machine hôte. Néanmoins, certains composants matériels/logiciels du Raspberry Pi utilisent une ancienne version de Raspberry Pi OS/Python, donc **une mise à jour complète reste un point d'amélioration**. |
| **6** | **Insufficient Privacy Protection** | Les données sont centralisées dans MongoDB et seules les informations nécessaires au fonctionnement du système sont stockées : badges, clients, visites, commandes, transactions, etc. L'accès à MongoDB nécessite une **authentification**. Les photos prises lors des visites sont également stockées sur l'infrastructure du projet plutôt que rendues directement accessibles depuis Internet. |
| **7** | **Insecure Data Transfer and Storage** | Les communications MQTT peuvent être effectuées via **TLS (8883)** afin de chiffrer les données en transit. MongoDB est protégé par un **compte administrateur et un mot de passe**. Les communications entre Raspberry Pi, MQTT, Node-RED et MongoDB ne sont donc pas simplement exposées sans contrôle d'accès. |
| **8** | **Lack of Device Management** | Chaque Raspberry Pi est identifié par un **`rpiId` unique** et associé à une table/emplacement. Le système publie notamment des informations de connexion (`smartcheers/rpi/connect/success`) contenant le `rpiId` et le `tableNumero`. Cela permet à Node-RED de savoir quel appareil est associé à quelle table et de contrôler les échanges MQTT. |
| **9** | **Insecure Default Settings** | Les services ne reposent pas sur les identifiants par défaut de MongoDB : un compte administrateur et un mot de passe sont configurés via les variables d'environnement. Node-RED dispose également d'une **authentification pour le portail employé**. Les services MongoDB sont exécutés dans Docker plutôt que d'être directement installés et exposés sans configuration de sécurité. |
| **10** | **Lack of Physical Hardening** | Le Raspberry Pi est utilisé comme équipement IoT dédié et les interfaces matérielles nécessaires au projet sont limitées aux composants utilisés (RFID, caméra, LCD, joystick, buzzer, etc.). Cependant, **aucun mécanisme avancé de hardening physique**, tel que Secure Boot, chiffrement complet du stockage, désactivation des interfaces de debug ou protection contre l'accès physique au Raspberry Pi, n'a été implémenté. Cette vulnérabilité reste donc principalement à améliorer. |



| Niveau de couverture | Vulnérabilités |
|---|---|
| 🟢 **Bien couvertes** | 1, 2, 3, 7, 8, 9 |
| 🟠 **Partiellement couvertes** | 5, 6 |
| 🔴 **À améliorer** | 4, 10 |

Les principales mesures de sécurité mises en œuvre dans Smart Cheers sont donc :
- authentification des services ;
- utilisation de variables d'environnement pour les secrets ;
- authentification MongoDB ;
- chiffrement MQTT avec TLS ;
- séparation des services sur plusieurs machines/VM ;
- identification unique des Raspberry Pi ;
- association Raspberry Pi ↔ table ;
- tokens pour isoler les dashboards des tables ;
- conteneurisation de MongoDB avec Docker ;
- limitation de l'exposition des services réseau.

Les deux principales lacunes restantes concernent le **processus de mise à jour sécurisé des appareils IoT** et le **hardening physique des Raspberry Pi**.
