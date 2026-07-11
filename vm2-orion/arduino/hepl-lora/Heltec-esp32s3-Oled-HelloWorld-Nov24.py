#include <Wire.h>  
#include "HT_SSD1306Wire.h"

static SSD1306Wire  display(0x3c, 500000, SDA_OLED, SCL_OLED, GEOMETRY_128_64, RST_OLED); // addr , freq , i2c group , resolution , rst



void VextON(void)
{
  pinMode(Vext,OUTPUT);
  digitalWrite(Vext, LOW);
}

void VextOFF(void) //Vext default OFF
{
  pinMode(Vext,OUTPUT);
  digitalWrite(Vext, HIGH);
}

void setup() {
  VextON();
  delay(100);
  display.init();
}

void loop() { 
  display.setContrast(255);
  display.setTextAlignment(TEXT_ALIGN_LEFT);
  display.clear();
  display.setFont(ArialMT_Plain_16);
  display.drawString(0,0,"Hello world");
  display.display();
  delay(2000);
}
