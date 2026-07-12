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


## ESP32 Heltec LoRa v3 envoi & LA66 recept
AT+CFG
```bash
Welcome to minicom 2.7

OPTIONS: I18n
Compiled on Apr 22 2017, 09:14:19.
Port /dev/ttyUSB0, 02:49:25

Press CTRL-A Z for help on special keys

AT

OK
AT+CFG
AT+FCU=0
AT+FCD=191
AT+FRE=868.100,868.100
AT+GROUPMOD=0,0
AT+BW=0,0
AT+SF=7,7
AT+POWER=14
AT+CRC=1,0
AT+HEADER=0,0
AT+CR=1,1
AT+IQ=0,0
AT+PREAMBLE=8,8
AT+SYNCWORD=0
AT+RXMOD=65535,2
AT+RXDAFORM=0
AT+WAITTIME=33554640


OK
```


```ino
#include "LoRaWan_APP.h"
#include "Arduino.h"

// --- CONFIGURATION ADAPTÉE AU LA66 ---
#define RF_FREQUENCY            868100000 // Correspond à AT+FRE=868.100
#define TX_OUTPUT_POWER         14        // Correspond à AT+POWER=14
#define LORA_BANDWIDTH          0         // [0: 125 kHz]
#define LORA_SPREADING_FACTOR   7         // [SF7]
#define LORA_CODINGRATE         1         // [1: 4/5]
#define LORA_PREAMBLE_LENGTH    8         // Correspond à AT+PREAMBLE=8
#define LORA_FIX_LENGTH_PAYLOAD_ON false
#define LORA_IQ_INVERSION_ON    false     // Correspond à AT+IQ=0
// -------------------------------------

#define BUFFER_SIZE             30 

char txpacket[BUFFER_SIZE];
double txNumber;
bool lora_idle = true;

static RadioEvents_t RadioEvents;

void setup() {
    Serial.begin(115200);
    Mcu.begin(HELTEC_BOARD, SLOW_CLK_TPYE);
    
    txNumber = 0;

    RadioEvents.TxDone = OnTxDone;
    RadioEvents.TxTimeout = OnTxTimeout;
    
    Radio.Init(&RadioEvents);
    Radio.SetChannel(RF_FREQUENCY);

    Radio.SetSyncWord(0x01);
    
    // Configuration de la modulation
    Radio.SetTxConfig(MODEM_LORA, TX_OUTPUT_POWER, 0, LORA_BANDWIDTH,
                      LORA_SPREADING_FACTOR, LORA_CODINGRATE,
                      LORA_PREAMBLE_LENGTH, LORA_FIX_LENGTH_PAYLOAD_ON,
                      true, 0, 0, LORA_IQ_INVERSION_ON, 3000); 
}

void loop() {
    if(lora_idle == true) {
        delay(2000); // Espacer les envois pour éviter de saturer
        txNumber += 0.01;
        // On envoie un message simple compatible avec le script Python du RPi
        sprintf(txpacket, "HELO%0.2f", txNumber); 
        
        Serial.printf("\r\nEnvoi: %s\r\n", txpacket);
        Radio.Send((uint8_t *)txpacket, strlen(txpacket));
        lora_idle = false;
    }
    Radio.IrqProcess();
}

void OnTxDone(void) {
    Serial.println("TX Terminé");
    lora_idle = true;
}

void OnTxTimeout(void) {
    Radio.Sleep();
    Serial.println("TX Timeout");
    lora_idle = true;
}
```
