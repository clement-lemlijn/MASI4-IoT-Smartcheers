# 🍻 SmartCheers – RaspberryPI - MINICOM

<img src="../assets/minicom.png" alt="Screenshot minicom" width="400" style="display: block; margin-left: auto; margin-right: auto;"/>

## Version
Le Raspberry Pi possède une ancienne version de minicom :
- minicom version 2.7 (compiled Apr 22 2017)
- Copyright (C) Miquel van Smoorenburg.

## Hardware 
LoRA-WAN branché sur le port `/dev/ttyUSB0`
```
ls -l /dev/ttyUSB0
```
`crw-rw---- 1 root dialout 188, 0 Jul  7 03:17 /dev/ttyUSB0`

## Minicom

Commandes : 
```
AT
ATI
AT+VER
AT+CGMR

```

Quitter : `Ctrl + A` puis `X`

Affichage : `sudo minicom -s` > `Screen and keyboard` > `Q`(Local echo), `R`(Line Wrap), `T`(Add carriage return).

Commandes disponibles : 
```
AT?
ATZ: Trig a reset of the MCU
AT+FDR: Reset Parameters to Factory Default
AT+CFG: Print all configurations
AT+FCU: Get or Set the Frame Counter Uplink
AT+FCD: Get or Set the Frame Counter Downlink
AT+FRE: Get or Set TX and RX frequency
AT+GROUPMOD: Get or Set TX and RX group
AT+BW: Get or Set TX and RX BandWidth
AT+SF: Get or Set TX and RX Spreading Factor
AT+POWER: Get or Set Tx Power Range
AT+CRC: Get or Set TX and RX CRC Type
AT+HEADER: Get or Set TX and RX Header Type
AT+CR: Get or Set TX and RX Header Type
AT+IQ: Get or Set TX and RX InvertIQ
AT+PREAMBLE: Get or Set TX and RX Preamble Length
AT+SYNCWORD: Get or Set sync word
AT+RXMOD: Get or Set Rx Timeout and Reply mode
AT+SEND: Send text data or hex along with the application port and confirm status
AT+RECV: Print last receive message, RSSI and SNR
AT+RXDAFORM: Get or Set Format received by RX
AT+WAITTIME: Get or set the takes time to return ACK in ms
```
