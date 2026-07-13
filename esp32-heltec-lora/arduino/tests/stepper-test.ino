#include <Stepper.h>

// Nombre de pas par tour pour un moteur 28BYJ-48 (généralement 2048)
const int stepsPerRevolution = 2048;

// Initialisation de la bibliothèque Stepper sur les broches 4, 5, 6, 7
// Note : L'ordre des pins dans le constructeur doit correspondre à la séquence 1-2-3-4
Stepper myStepper(stepsPerRevolution, 7, 5, 6, 4);

void setup() {
  // Vitesse de rotation en tours par minute
  myStepper.setSpeed(10);
  
  Serial.begin(115200);
}

void loop() {
  // Faire tourner le moteur dans un sens
  Serial.println("Rotation sens horaire");
  myStepper.step(stepsPerRevolution);
  delay(1000);

  // Faire tourner le moteur dans l'autre sens
  Serial.println("Rotation sens anti-horaire");
  myStepper.step(-stepsPerRevolution);
  delay(1000);
}
