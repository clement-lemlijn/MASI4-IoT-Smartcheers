# GitHub Actions Runner sur Raspberry Pi

Ce document détaille la configuration de mon Self-hosted Runner installé sur le Raspberry Pi. Il permet d'automatiser le déploiement du code SmartCheer's.

## Architecture
- Plateforme : Raspberry Pi (Architecture ARM)
- Localisation : ~/smartcheers/actions-runner/
- Mode : Service système (systemd) pour démarrage automatique au boot.

## Gestion du service
```
sudo ./svc.sh status
```
```
sudo ./svc.sh stop
```
```
sudo ./svc.sh start
```
```
sudo ./svc.sh uninstall
```
## Pipeline de déploiement (CI/CD)
Le fichier de workflow se trouve dans .github/workflows/deploy.yml. Dès qu'un git push est effectué sur la branche main, le pipeline
Exécute la mise à jour du code local sur le Raspberry Pi :
```
cd /home/pi/smartcheers && git pull origin main
```

## Dépannage
- Logs : Les logs du runner sont disponibles dans le dossier ~/smartcheers/actions-runner/_diag/
- Service : `` journalctl -u smartcheers.service -n 50 --no-pager ``

### Runner corrompu
```
cd ~/smartcheers/actions-runner
sudo ./svc.sh stop
sudo ./svc.sh uninstall
rm .runner .credentials .credentials_rsaparams
# GitHub Settings > Actions > Runners, "New self-hosted runner"
./config.sh --url https://github.com/clement-lemlijn/MASI4-IoT-Smartcheers --token <NOUVEAU_TOKEN>
sudo ./svc.sh install
sudo ./svc.sh start
```
