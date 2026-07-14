# 🍻 SmartCheers – ESP32 Heltec LoRa

<img src="../assets/esp32-heltec-lora.jpg" alt="Esp32 Heltec Lora" width="400" style="display: block; margin-left: auto; margin-right: auto;"/>

## Hardware & OS



```
python -m serial.tools.miniterm COM6 115200
```
## Erasing
```
pip install esptool
esptool erase_flash


esptool --baud 460800 write_flash 0 ESP32_GENERIC_S3-20260406-v1.28.0.bin
```

## Utilisation d'une alimentation externe

Attention, lors de l'utilisation d'une alimentation externe, permettant de brancher un servo moteur et un stepper motor sur le même esp32 par exemple, bien penser à relier les terres ensemble.

Pourquoi ? _Le signal PWM de l'ESP32 envoie des impulsions de 3.3V. Pour que le servo "comprenne" ces impulsions, il doit comparer cette tension à une référence de masse commune. Sans cette connexion, le signal est "flottant" et le servo peut ignorer les commandes ou réagir de manière erratique_

Attention tout de même, brancher la borne GND de l'ESP32 sur un autre GND peut causer des problèmes de connections COM9 avec windows -_-
