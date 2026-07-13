#include <NewPing.h>

// Définition des broches
#define TRIGGER_PIN  20  // Broche SIG connectée au GPIO 20
#define ECHO_PIN     20  // Pour un capteur à 3 broches, le SIG sert aux deux
#define MAX_DISTANCE 400 // Distance maximale en cm

// Initialisation de NewPing
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

void setup() {
  Serial.begin(115200);
}

void loop() {
  delay(50); // Attente de 50ms entre chaque mesure
  
  unsigned int uS = sonar.ping(); // Envoi du ping et mesure du temps
  
  // Conversion du temps en distance (en cm)
  // 0 signifie hors de portée
  Serial.print("Distance: ");
  if (uS == 0) {
    Serial.println("Hors de portée");
  } else {
    Serial.print(uS / US_ROUNDTRIP_CM);
    Serial.println(" cm");
  }
}
