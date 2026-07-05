# 🍻 SmartCheers – VM2 ORION

<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRRgmNospvsJiLQeFw17OLJlSLajjJ2_FhLp1XcOPPspg&s=10" alt="Photo VmWare" width="400" style="display: block; margin-left: auto; margin-right: auto;"/>

## Architecture 
Ubuntu64-bit

## Connexion
User : "LEMLIJN Clément"
Password : ""

## Services
### MQTT Broker
```
cd MASI4-IoT-Smartcheers/vm2-orion/mqtt-broker/
sudo docker exec -it mosquitto mosquitto_sub -t '$SYS/#' -C 1 -u clement-lemlijn -P mqtt-pwd
```


## Others 
```
sudo nano /etc/hosts
```
