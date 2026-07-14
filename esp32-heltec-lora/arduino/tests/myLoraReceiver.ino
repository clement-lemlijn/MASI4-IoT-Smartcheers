#include "LoRaWan_APP.h"
#include "Arduino.h"

// --- CONFIGURATION (Doit correspondre exactement au LA66) ---
#define RF_FREQUENCY          868100000 
#define TX_OUTPUT_POWER       14        
#define LORA_BANDWIDTH        0         
#define LORA_SPREADING_FACTOR 7         
#define LORA_CODINGRATE       1         
#define LORA_PREAMBLE_LENGTH  8         
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
    
    // Configuration identique au LA66 pour le dialogue
    Radio.SetRxConfig(MODEM_LORA, LORA_BANDWIDTH, LORA_SPREADING_FACTOR,
                      LORA_CODINGRATE, 0, LORA_PREAMBLE_LENGTH,
                      10, false, 0, true, 0, 0, LORA_IQ_INVERSION_ON, true);
    
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
