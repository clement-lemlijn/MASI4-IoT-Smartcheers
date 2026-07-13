#include <ESP32Servo.h>

Servo monServo;
int servoPin = 1; // Choisissez un GPIO libre

void setup() {
  // Nécessaire pour les ESP32
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  
  monServo.setPeriodHertz(50); // Standard pour les servos
  monServo.attach(servoPin, 500, 2400); // Impulsions min/max
}

void loop() {
  monServo.write(0);   // Position 0 degrés
  delay(1000);
  monServo.write(90);  // Position 90 degrés
  delay(1000);
  monServo.write(180); // Position 180 degrés
  delay(1000);
}
