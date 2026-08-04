#include "LoRaWan_APP.h"
#include <ESP32Servo.h>
#include <Stepper.h>
#include <NewPing.h>
#include <Wire.h>
#include "HT_SSD1306Wire.h"

SSD1306Wire myOLED(
    0x3c,
    500000,
    SDA_OLED,
    SCL_OLED,
    GEOMETRY_128_64,
    RST_OLED
);

Servo monServo;


// --- VARIABLES ---
bool isRunning = false;
const int stepsPerRevolution = 2048; // Pour le stepper motor
unsigned long lastDistanceCheck = 0;
unsigned long lastSerialUpdate = 0; // Timer pour le série/écran
int currentDist = 0;

// --- KEEPALIVE / DEBUG LORA ---
unsigned long lastKeepAlive = 0;
const unsigned long KEEPALIVE_INTERVAL = 5000; // ms entre chaque keepalive
unsigned int keepAliveCounter = 0;
String lastRadioMsg = "Aucun";   // Dernier message reçu OU envoyé, pour l'écran
bool radioBusySending = false;   // Empêche de renvoyer pendant une transmission en cours

// --- ACK STATUS ---
bool lastAckOk = false;
bool waitingForAck = false;
unsigned long lastAckTime = 0;
const unsigned long ACK_TIMEOUT = 2500; // 2,5 secondes max pour recevoir l'ACK

// --- CONFIGURATION RADIO ---
static RadioEvents_t RadioEvents;
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

// --- INIT ULTRASOUND ---
#define TRIGGER_PIN  20
#define ECHO_PIN     20
#define MAX_DISTANCE 400 // Distance maximale en cm
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);


void updateDisplay(String status, int dist) {
    myOLED.clear();

    // ===== Ligne 1 : Status train =====
    myOLED.setFont(ArialMT_Plain_16);
    myOLED.setTextAlignment(TEXT_ALIGN_LEFT);
    myOLED.drawString(0, 0, "Train: " + status);

    // ===== Haut droite : Icône radio + V / X =====
    myOLED.setFont(ArialMT_Plain_10);
    myOLED.setTextAlignment(TEXT_ALIGN_RIGHT);

    // Gestion du timeout ACK
    if (waitingForAck && (millis() - lastKeepAlive > ACK_TIMEOUT)) {
        lastAckOk = false;
        waitingForAck = false;
    }

    if (lastAckOk) {
        myOLED.drawString(128, 0, "LoRa V");   // ACK OK
    } else {
        myOLED.drawString(128, 0, "LoRa X");   // Pas d'ACK
    }

    // ===== Distance =====
    myOLED.setFont(ArialMT_Plain_16);
    myOLED.setTextAlignment(TEXT_ALIGN_LEFT);
    myOLED.drawString(0, 22, "Dist: " + String(dist) + " cm");

    // ===== Dernier message LoRa =====
    myOLED.setFont(ArialMT_Plain_10);
    myOLED.drawString(0, 44, lastRadioMsg);

    // ===== Compteur Keepalive =====
    myOLED.drawString(0, 54, "KA #" + String(keepAliveCounter));

    myOLED.display();
}

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

        digitalWrite(26, LOW);
        pulseHigh = false;

        // Attendre le reste des 20ms
        timerAlarm(timer, 20000 - pulseWidth, true, 0);
    } else {
        // Début de l'impulsion HIGH
        digitalWrite(26, HIGH);
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

int measureCmUltrasound(bool isVerbose = false){
  unsigned int uS = sonar.ping(); // Envoi du ping et mesure du temps
  // Conversion du temps en distance (en cm)
  // 0 signifie hors de portée
  if(isVerbose){
    Serial.print("Distance: ");
    if (uS == 0) {
      Serial.println("Hors de portée");
      return 0;
    } else {
      Serial.print(uS / US_ROUNDTRIP_CM);
      Serial.println(" cm");
    }
  }
  if(uS == 0) return 0;
  return uS / US_ROUNDTRIP_CM;
}

// Construit et envoie un message de keepalive/debug par LoRa
void sendKeepAlive() {
    if (radioBusySending) return;

    keepAliveCounter++;
    String status = isRunning ? "RUN" : "STOP";
    String msg = "KEEPALIVE;CNT=" + String(keepAliveCounter) +
                 ";STATUS=" + status +
                 ";DIST=" + String(currentDist);

    Serial.println("[LoRa TX] " + msg);
    lastRadioMsg = "TX> " + msg;

    // On attend un ACK
    waitingForAck = true;
    lastAckOk = false;

    radioBusySending = true;
    Radio.Send((uint8_t *)msg.c_str(), msg.length());
}

void setup() {
    Serial.begin(115200);
    Mcu.begin(HELTEC_BOARD, SLOW_CLK_TPYE);
    myStepper.setSpeed(10);

    // Alimentation de l'écran OLED
    pinMode(Vext, OUTPUT);
    digitalWrite(Vext, LOW);
    delay(100);

    myOLED.init();
    myOLED.flipScreenVertically();
    myOLED.setContrast(255);
    myOLED.clear();
    myOLED.display();

    showStartupScreenStart();

//    // Setup Servo
//    pinMode(21, OUTPUT);
//    timer = timerBegin(1000000);     // Timer à 1MHz : 1 tick = 1µs
//    timerAttachInterrupt(timer, &onTimer);
//    timerAlarm(timer, 20000, true, 0);     // Démarrage du signal servo
//    setServoAngle(0);
//    Serial.println("Servo position 0°");

    delay(1000);

    // Setup Radio
    RadioEvents.RxDone = OnRxDone;
    RadioEvents.TxDone = OnTxDone;
    RadioEvents.TxTimeout = OnTxTimeout;
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
    showStartupScreenReady();
    delay(1000);

    // Setup Servo
    pinMode(26, OUTPUT);
    timer = timerBegin(1000000);     // Timer à 1MHz : 1 tick = 1µs
    timerAttachInterrupt(timer, &onTimer);
    timerAlarm(timer, 20000, true, 0);     // Démarrage du signal servo
    setServoAngle(0);
    Serial.println("Servo position 0°");

}

void loop() {
    Radio.IrqProcess();
  
    // 1. Détection obstacle (chaque 100ms)
    currentDist = measureCmUltrasound();
    if (isRunning && currentDist > 0 && currentDist < 15) {
        stopTrain();
    }

    // 2. Keepalive/debug LoRa (toutes les KEEPALIVE_INTERVAL ms)
    if (!radioBusySending && millis() - lastKeepAlive > KEEPALIVE_INTERVAL) {
        sendKeepAlive();
        lastKeepAlive = millis();
    }

    // 3. Mise à jour écran et Série (chaque 500ms pour ne pas saturer)
    if (millis() - lastSerialUpdate > 500) {
        String status = isRunning ? "ROULE" : "ARRET";
        updateDisplay(status, currentDist);
        Serial.printf("Status: %s | Distance: %d cm\r\n", status.c_str(), currentDist);
        lastSerialUpdate = millis();
    }

    delay(50);
}

void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr) {
    String message = "";
    for (int i = 0; i < size; i++) {
        message += (char)payload[i];
    }

    Serial.println("========== RX ==========");
    Serial.println(message);
    Serial.printf("RSSI: %d | SNR: %d | size: %d\n", rssi, snr, size);
    Serial.println("========================");

    lastRadioMsg = "RX> " + message + " (" + String(rssi) + "dBm)";

    // Détection de l'ACK (attention : tu reçois "KEEPALIVEACK" sans underscore)
    if (message == "KEEPALIVEACK" || message == "KEEPALIVE_ACK") {
        lastAckOk = true;
        waitingForAck = false;
        lastAckTime = millis();
        Serial.println(">>> ACK reçu du Raspberry !");
    }
    else if (message == "TRAINSTART" && !isRunning) {
        startTrain();
    }
    else if (message == "TRAINSTOP") {
        stopTrain();
    }

    Radio.Rx(0);
}

// Appelé automatiquement quand une transmission (ex: keepalive) est terminée.
// On repasse en écoute continue pour ne pas rater les commandes TRAINSTART/TRAINSTOP.
void OnTxDone(void) {
    Serial.println("[LoRa] Envoi termine, retour en reception");
    radioBusySending = false;
    Radio.Rx(0);
}

void OnTxTimeout(void) {
    Serial.println("[LoRa] Timeout d'envoi");
    radioBusySending = false;
    Radio.Rx(0);
}

void OnRxError(void) {
    Serial.println("Erreur de reception");
    Radio.Rx(0);
}

void OnRxTimeout(void) {
    Radio.Rx(0);
}

void showStartupScreenStart() {

    myOLED.setTextAlignment(TEXT_ALIGN_LEFT);

    // =====================================================
    // Animation du cadre
    // =====================================================
    for (int i = 0; i <= 30; i += 2) {
        myOLED.clear();
        myOLED.drawRect(i, i / 2, 128 - 2 * i, 64 - i);
        myOLED.display();
        delay(18);
    }

    delay(150);

    // =====================================================
    // Logo SmartCheers
    // =====================================================
    myOLED.clear();

    // Train
    myOLED.fillCircle(20, 42, 3);
    myOLED.fillCircle(40, 42, 3);
    myOLED.fillCircle(60, 42, 3);

    myOLED.fillRect(14, 28, 52, 12);
    myOLED.fillRect(46, 18, 18, 10);
    myOLED.fillRect(18, 18, 5, 10);

    // Fumée
    myOLED.drawCircle(18, 12, 2);
    myOLED.drawCircle(23, 8, 2);
    myOLED.drawCircle(28, 5, 2);

    // Texte centré
    myOLED.setTextAlignment(TEXT_ALIGN_CENTER);

    myOLED.setFont(ArialMT_Plain_16);
    myOLED.drawString(96, 6, "SMART");

    myOLED.setFont(ArialMT_Plain_10);
    myOLED.drawString(96, 24, "CHEERS");
    myOLED.drawString(96, 40, "Autonomous");
    myOLED.drawString(96, 52, "Train");

    myOLED.display();

    delay(1700);

    // =====================================================
    // Chargement
    // =====================================================
    myOLED.clear();

    myOLED.setTextAlignment(TEXT_ALIGN_CENTER);

    myOLED.setFont(ArialMT_Plain_16);
    myOLED.drawString(64, 4, "SMARTCHEERS");

    myOLED.setFont(ArialMT_Plain_10);
    myOLED.drawString(64, 22, "Boot sequence");


    // Barre
    myOLED.drawRect(14, 34, 100, 10);
    
    for (int i = 0; i <= 100; i += 4) {
    
        myOLED.setColor(BLACK);
        myOLED.fillRect(16, 36, 96, 6);
        myOLED.fillRect(46, 44, 40, 8);
        myOLED.setColor(WHITE);
    
        myOLED.fillRect(16, 36, i * 96 / 100, 6);
    
        myOLED.drawString(64, 44, String(i) + "%");
    
        myOLED.display();
        delay(35);
    }
    
    delay(500);

}

void showStartupScreenReady() {

    // =====================================================
    // Ready
    // =====================================================
    myOLED.clear();

    myOLED.setTextAlignment(TEXT_ALIGN_CENTER);

    myOLED.setFont(ArialMT_Plain_16);
    myOLED.drawString(64, 8, "READY");

    myOLED.setFont(ArialMT_Plain_10);
    myOLED.drawString(64, 30, "SmartCheers Train");
    myOLED.drawString(64, 44, "Ready for service");

    myOLED.display();

    delay(2000);
}
