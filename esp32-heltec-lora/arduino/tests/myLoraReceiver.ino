#include "LoRaWan_APP.h"
#include "Arduino.h"

// --- CONFIGURATION (Doit correspondre exactement au LA66) ---
#define RF_FREQUENCY          868100000 
#define TX_OUTPUT_POWER       14        
#define LORA_BANDWIDTH        0         
#define LORA_SPREADING_FACTOR 7         
#define LORA_CODINGRATE       1         
#define LORA_PREAMBLE_LENGTH  8        
#define LORA_FIX_LENGTH_PAYLOAD_ON false 
#define LORA_IQ_INVERSION_ON  false     

static RadioEvents_t RadioEvents;

void setup() {
    Serial.begin(115200);
    Mcu.begin(HELTEC_BOARD, SLOW_CLK_TPYE);
    
    // Initialisation des callbacks
    RadioEvents.RxDone = OnRxDone;
    RadioEvents.RxError = OnRxError;
    RadioEvents.RxTimeout = OnRxTimeout;
    
    Radio.Init(&RadioEvents);
    Radio.SetChannel(RF_FREQUENCY);
    
    Radio.SetTxConfig(MODEM_LORA, TX_OUTPUT_POWER, 0, LORA_BANDWIDTH,
                      LORA_SPREADING_FACTOR, LORA_CODINGRATE,
                      LORA_PREAMBLE_LENGTH, LORA_FIX_LENGTH_PAYLOAD_ON,
                      true, 0, 0, LORA_IQ_INVERSION_ON, 3000); 


    Radio.SetRxConfig(
      MODEM_LORA,
      LORA_BANDWIDTH,          // bandwidth = 125 kHz
      LORA_SPREADING_FACTOR,   // datarate = SF7
      LORA_CODINGRATE,         // coderate = 4/5
      0,                       // bandwidthAfc (ignoré en LoRa)
      LORA_PREAMBLE_LENGTH,    // préambule = 8
      0,                       // timeout symbole
      LORA_FIX_LENGTH_PAYLOAD_ON,
      0,                       // longueur payload (0 = variable)
      true,                    // CRC ON
      false,                   // Frequency hopping OFF
      0,                       // hop period
      LORA_IQ_INVERSION_ON,
      true                     // RX continu
  );

    Serial.println("ESP32 Pret : En attente de messages LoRa...");
    
    // Lancer la réception infinie
    Radio.Rx(0); 
}

void loop() {
    // La radio gère tout en arrière-plan via les interruptions
    Radio.IrqProcess();
}

// Callback appelé quand un message arrive
void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr) {
    Serial.print("Message recu : ");
    for (int i = 0; i < size; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.printf(" | RSSI: %d dBm, SNR: %d\n", rssi, snr);
    
    // Relancer l'écoute immédiatement
    Radio.Rx(0);
}

void OnRxError(void) {
    Serial.println("Erreur de reception");
    Radio.Rx(0);
}

void OnRxTimeout(void) {
    Radio.Rx(0);
}





// MINICOM : AT+SEND=1,0,BonjourESP32










