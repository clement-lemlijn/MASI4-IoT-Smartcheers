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


esptool --baud 460800 write_flash 0 LA66_P2P_v1.2.bin
```
