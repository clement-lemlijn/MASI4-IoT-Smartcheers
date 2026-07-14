
#include "LoRaWan_APP.h"
#include <ESP32Servo.h>
#include <Stepper.h>
#include <NewPing.h>
#include "HT_SSD1306Wire.h"

// --- CONFIGURATIONS ---
// Pins (À ADAPTER selon ton câblage réel)
#define SERVO_PIN 18
#define STEPPER_PIN1 19
#define STEPPER_PIN2 21
#define STEPPER_PIN3 22
#define STEPPER_PIN4 23
#define TRIG_PIN 32
#define ECHO_PIN 33

// LoRa
#define RF_FREQUENCY 868100000

// SSD1306Wire display(0x3c, 500000, SDA_OLED, SCL_OLED, GEOMETRY_128_64, RST_OLED);
SSD1306Wire myOLED(0x3c, 500000, SDA_OLED, SCL_OLED, GEOMETRY_128_64, RST_OLED);

Servo monServo;
Stepper myStepper(2048, STEPPER_PIN1, STEPPER_PIN3, STEPPER_PIN2, STEPPER_PIN4);
NewPing sonar(TRIG_PIN, ECHO_PIN, 400);


// --- VARIABLES ---
bool isRunning = false;
unsigned long lastDistanceCheck = 0;
char rx_buffer[30];

void updateDisplay(String status) {
    myOLED.clear();
    myOLED.setFont(ArialMT_Plain_16);
    myOLED.drawString(0, 0, "Train LEGO");
    myOLED.drawString(0, 25, "Statut: " + status);
    myOLED.display();
}

void stopTrain() {
    isRunning = false;
    // Mouvement d'arrêt (Servo appuie sur le bouton)
    monServo.write(10);
    delay(500);
    monServo.write(0);
    
    // Envoi LoRa TRAIN_STOPPED
    Radio.Send((uint8_t *)"TRAIN_STOPPED", 13);
    updateDisplay("ARRET");
}

void startTrain() {
    isRunning = true;
    myStepper.step(1024); // Révolution pour démarrer
    updateDisplay("EN MARCHE");
}

void setup() {
    Serial.begin(115200);
    Mcu.begin(HELTEC_BOARD, SLOW_CLK_TPYE);
    
    // OLED
    pinMode(Vext, OUTPUT); 
    digitalWrite(Vext, LOW); 
    delay(100);
    myOLED.init(); 
    myOLED.flipScreenVertically();
    
    // Servo
    ESP32PWM::allocateTimer(0);
    monServo.attach(SERVO_PIN);
    monServo.write(0);
    
    // LoRa
    Radio.Init(NULL);
    Radio.SetChannel(RF_FREQUENCY);
    Radio.Rx(0); // Passer en mode réception continue
    
    updateDisplay("PRET");
}

void loop() {
    Radio.IrqProcess();

    // Logique de détection obstacle (tous les 100ms)
    if (isRunning && millis() - lastDistanceCheck > 100) {
        int dist = sonar.ping_cm();
        if (dist > 0 && dist < 15) {
            stopTrain();
        }
        lastDistanceCheck = millis();
    }
}

// Callback LoRa quand un message est reçu
void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr) {
    String message = "";
    for(int i=0; i<size; i++) message += (char)payload[i];
    
    if (message == "TRAIN_START" && !isRunning) {
        startTrain();
    } else if (message == "TRAIN_STOP" && isRunning) {
        stopTrain();
    }
}
