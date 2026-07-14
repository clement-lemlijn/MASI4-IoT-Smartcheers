#define SERVO_PIN 21

hw_timer_t *timer = NULL;

volatile bool pulseHigh = false;
volatile int pulseWidth = 1500; // µs


void IRAM_ATTR onTimer() {

    if (pulseHigh) {

        digitalWrite(SERVO_PIN, LOW);
        pulseHigh = false;

        // reste de la période
        timerAlarm(timer, 20000 - pulseWidth, true, 0);

    } else {

        digitalWrite(SERVO_PIN, HIGH);
        pulseHigh = true;

        timerAlarm(timer, pulseWidth, true, 0);

    }
}


void setup() {

    Serial.begin(115200);

    pinMode(SERVO_PIN, OUTPUT);

    timer = timerBegin(1000000); // 1 MHz

    timerAttachInterrupt(timer, &onTimer);

    timerAlarm(timer, 20000, true, 0);

}


void loop() {

    // exemple : position servo
    pulseWidth = 1000;
    delay(2000);

    pulseWidth = 1500;
    delay(2000);

    pulseWidth = 2000;
    delay(2000);
}
