


```
lemlijn-clement@VM-Orion:~$ sudo docker exec -it mosquitto mosquitto_sub -t "smartcheers/orders/new" -u clement-lemlijn -P mqtt-pwd
"{\"rpiId\": \"rpi-002\", \"badgeUid\": \"\\u000227004228D09D\\u0003\", \"command\": [{\"produitId\": \"a2138356-7baf-4142-b468-02b7fbca4253\", \"quantite\": 1}]}"
^Clemlijn-clement@VM-Orion:~sudo docker exec -it mosquitto mosquitto_sub -t "smartcheers/orders/preparation" -u clement-lemlijn -P mqtt-pwd
{"orderId":"6a770291a009b102e3a758a3"}
^Clemlijn-clement@VM-Orion:~sudo docker exec -it mosquitto mosquitto_sub -t "smartcheers/orders/ready" -u clement-lemlijn -P mqtt-pwd
{"orderId":"6a770291a009b102e3a758a3"}
^Clemlijn-clement@VM-Orion:~sudo docker exec -it mosquitto mosquitto_sub -t "smartcheers/orders/envoyee" -u clement-lemlijn -P mqtt-pwd
{"orderId":"6a770291a009b102e3a758a3"}

```
