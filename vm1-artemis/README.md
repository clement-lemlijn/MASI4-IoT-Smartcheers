# 🍻 SmartCheers – VM2 ARTEMIS

<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRRgmNospvsJiLQeFw17OLJlSLajjJ2_FhLp1XcOPPspg&s=10" alt="Photo VmWare" width="400" style="display: block; margin-left: auto; margin-right: auto;"/>

## Architecture
Ubuntu64-bit

## Connexion
User : "LEMLIJN Clément"
Password : ""

## Creation user mdp & init depuis shell conteneur
`sudo docker exec -it mongodb-smartcheers mongosh -u admin -p 'TON_MOT_DE_PASSE_ROOT' --authenticationDatabase admin`

## Install mongodb compass on VM 
```
wget https://downloads.mongodb.com/compass/mongodb-compass_1.44.4_amd64.deb
sudo apt install ./mongodb-compass_1.44.4_amd64.deb
```