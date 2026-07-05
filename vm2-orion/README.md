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

## Network
Configuration netplan pour avoir une ip statique `192.168.87.140`.

```yaml
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: no
      addresses:
        - 192.168.87.140/24
      routes:
        - to: default
          via: 192.168.87.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 1.1.1.1
```
_`/etc/netplan/50-cloud-init.yaml`_
## Others 
```
sudo nano /etc/hosts
```
