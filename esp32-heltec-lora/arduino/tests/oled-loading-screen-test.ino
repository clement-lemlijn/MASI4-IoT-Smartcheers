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

void showStartupScreen();

void setup() {
    // Alimentation de l'écran OLED
    pinMode(Vext, OUTPUT);
    digitalWrite(Vext, LOW);
    delay(100);

    myOLED.init();
    myOLED.flipScreenVertically();
    myOLED.setContrast(255);
    myOLED.clear();
    myOLED.display();

    showStartupScreen();
}

void loop() {
}

void showStartupScreen() {

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
