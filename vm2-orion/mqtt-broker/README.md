# 🍻 SmartCheers – MQTT Broker

<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ6NhNdVE-dXYfehEXKqhrUTsrke_Ium2IiKBW_ExPLdA&s=10" alt="Photo MQTT" width="400" style="display: block; margin-left: auto; margin-right: auto;"/>

## Start : 
```
sudo docker compose restart
```

## Service check : 
```
sudo docker compose ps
sudo ss -tulpn | grep mosquitto
docker exec -it mosquitto mosquitto_sub -t '$SYS/#' -C 1
```

## add user : 
```
sudo docker exec -it mosquitto mosquitto_passwd -c /mosquitto/config/pwfile ton_user
```
