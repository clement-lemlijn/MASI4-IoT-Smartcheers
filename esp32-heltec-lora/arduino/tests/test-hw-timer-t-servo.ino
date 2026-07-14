#define SERVO_PIN 21

/*


Pour un servo classique :

0° ≈ 500 µs
50° ≈ 1000 µs environ (ça dépend du servo)
90° ≈ 1500 µs

Voici un script qui :

initialise le servo à 0°
attend 1 seconde
fait des allers-retours 0° ↔ 50° toutes les 2 secondes



*/

hw_timer_t *timer = NULL;

volatile bool pulseHigh = false;
volatile int pulseWidth = 500; // position 0° au démarrage


void IRAM_ATTR onTimer() {

    if (pulseHigh) {

        // Fin de l'impulsion HIGH
        digitalWrite(SERVO_PIN, LOW);
        pulseHigh = false;

        // Attendre le reste des 20ms
        timerAlarm(timer, 20000 - pulseWidth, true, 0);

    } else {

        // Début de l'impulsion HIGH
        digitalWrite(SERVO_PIN, HIGH);
        pulseHigh = true;

        // Durée de l'impulsion selon position
        timerAlarm(timer, pulseWidth, true, 0);
    }
}


// Conversion angle -> largeur impulsion
void setServoAngle(int angle) {

    // 0° = 500us
    // 180° = 2500us
    pulseWidth = map(angle, 0, 180, 500, 2500);
}


void setup() {

    Serial.begin(115200);

    pinMode(SERVO_PIN, OUTPUT);

    // Timer à 1MHz : 1 tick = 1µs
    timer = timerBegin(1000000);

    timerAttachInterrupt(timer, &onTimer);

    // Démarrage du signal servo
    timerAlarm(timer, 20000, true, 0);


    // Position initiale 0°
    setServoAngle(0);

    Serial.println("Servo position 0°");

    delay(1000);
}


void loop() {

    // Aller à 50°
    setServoAngle(50);
    Serial.println("Servo 50°");
    delay(2000);


    // Retour à 0°
    setServoAngle(0);
    Serial.println("Servo 0°");
    delay(2000);
}
