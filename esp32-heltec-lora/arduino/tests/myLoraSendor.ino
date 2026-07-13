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
