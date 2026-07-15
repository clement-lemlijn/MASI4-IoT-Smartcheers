#include "LoRaWan_APP.h"
#include <ESP32Servo.h>
#include <Stepper.h>
#include <NewPing.h>
#include "HT_SSD1306Wire.h"

// --- CONFIGURATIONS ---
#define TRIG_PIN 32
#define ECHO_PIN 33
//
//SSD1306Wire myOLED(0x3c, 500000, SDA_OLED, SCL_OLED, GEOMETRY_128_64, RST_OLED);
Servo monServo;
//NewPing sonar(TRIG_PIN, ECHO_PIN, 400);
static RadioEvents_t RadioEvents;


// --- VARIABLES ---
bool isRunning = false;
const int stepsPerRevolution = 2048; // Pour le stepper motor
unsigned long lastDistanceCheck = 0;
unsigned long lastSerialUpdate = 0; // Nouveau timer pour le série/écran
int currentDist = 0;


// --- CONFIGURATION RADIO ---
#define RF_FREQUENCY          868100000 
#define TX_OUTPUT_POWER       14        
#define LORA_BANDWIDTH        0         
#define LORA_SPREADING_FACTOR 7         
#define LORA_CODINGRATE       1         
#define LORA_PREAMBLE_LENGTH  8        
#define LORA_FIX_LENGTH_PAYLOAD_ON false 
#define LORA_IQ_INVERSION_ON  false    

// --- INIT STEPPER MOTOR ---
Stepper myStepper(stepsPerRevolution, 7, 5, 6, 4);

// --- INIT SERVO ---
hw_timer_t *timer = NULL;
volatile bool pulseHigh = false;
volatile int pulseWidth = 500;


//void updateDisplay(String status, int dist) {
//    myOLED.clear();
//    myOLED.setFont(ArialMT_Plain_16);
//    myOLED.drawString(0, 0, "Train: " + status);
//    myOLED.drawString(0, 25, "Dist: " + String(dist) + " cm");
//    myOLED.display();
//}

void stopTrain() {
    // if(!isRunning) return; // Évite les doubles arrêts // En fait non xD
    isRunning = false;
    setServoAngle(50);
    delay(500);
    setServoAngle(0);
//    Radio.Send((uint8_t *)"TRAINSTOPPED", 13);
    Serial.println("Train arrete par obstacle ou commande");
}

void startTrain() {
    isRunning = true;
    Serial.println("Le train demarre");
    myStepper.step(-stepsPerRevolution/6); // (nég. car stepper à l'envers)
    Serial.println("Le train a demarre");
}

// Servo 
void IRAM_ATTR onTimer() {
    if (pulseHigh) {

        digitalWrite(21, LOW);
        pulseHigh = false;

        // Attendre le reste des 20ms
        timerAlarm(timer, 20000 - pulseWidth, true, 0);
    } else {
        // Début de l'impulsion HIGH
        digitalWrite(21, HIGH);
        pulseHigh = true;
        // Durée de l'impulsion selon position
        timerAlarm(timer, pulseWidth, true, 0);
    }
}
void setServoAngle(int angle) {

    // 0° = 500us
    // 180° = 2500us
    pulseWidth = map(angle, 0, 180, 500, 2500);
}

void setup() {
    Serial.begin(115200);
    Mcu.begin(HELTEC_BOARD, SLOW_CLK_TPYE);
    myStepper.setSpeed(10);

//    pinMode(Vext, OUTPUT); digitalWrite(Vext, LOW); delay(100);
//    myOLED.init(); myOLED.flipScreenVertically();
//    

    // Setup Servo
    pinMode(21, OUTPUT);
    timer = timerBegin(1000000);     // Timer à 1MHz : 1 tick = 1µs
    timerAttachInterrupt(timer, &onTimer);
    timerAlarm(timer, 20000, true, 0);     // Démarrage du signal servo
    setServoAngle(0);
    Serial.println("Servo position 0°");
    delay(1000);
    
    // Setup Radio
    RadioEvents.RxDone = OnRxDone;
    // RadioEvents.RxError = OnRxError;
    // RadioEvents.RxTimeout = OnRxTimeout;
    
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
    Serial.println("[Smartcheers-Lego-Train.ino] ESP32 Pret : En attente de messages LoRa...");

    Radio.Rx(0); 
}

void loop() {
    Radio.IrqProcess();

//    // 1. Détection obstacle (chaque 100ms)
//    if (millis() - lastDistanceCheck > 100) {
//        currentDist = sonar.ping_cm();
//        if (isRunning && currentDist > 0 && currentDist < 15) {
//            stopTrain();
//        }
//        lastDistanceCheck = millis();
//    }
//
//    // 2. Mise à jour écran et Série (chaque 500ms pour ne pas saturer)
//    if (millis() - lastSerialUpdate > 500) {
//        String status = isRunning ? "ROULE" : "ARRET";
//        updateDisplay(status, currentDist);
//        Serial.printf("Status: %s | Distance: %d cm\r\n", status.c_str(), currentDist);
//        lastSerialUpdate = millis();
//    }
}

void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr) {
    String message = "";

    Serial.print("ASCII : ");
    for (int i = 0; i < size; i++){
        message += (char)payload[i];
        Serial.print((char)payload[i]);
      }
    Serial.println();
    Serial.println(message);
    if (message == "TRAINSTART" && !isRunning) startTrain();
    else if (message == "TRAINSTOP" && isRunning) stopTrain();

    Radio.Rx(0);
}

//void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr) {
//    Serial.println("OnRxDone");
//    String message = "";
//    for(int i=0; i<size; i++) message += (char)payload[i];
//    Serial.println("Message : " + message);
//    if (message == "TRAINSTART" && !isRunning) startTrain();
//    else if (message == "TRAINSTOP" && isRunning) stopTrain();
//}

void OnRxError(void) {
    Serial.println("Erreur de reception");
    Radio.Rx(0);
}

void OnRxTimeout(void) {
    Radio.Rx(0);
}
