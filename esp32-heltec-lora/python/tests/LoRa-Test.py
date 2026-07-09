from machine import Pin, SoftI2C
import time
from ssd1306 import SSD1306_I2C


# Activation OLED
vext = Pin(36, Pin.OUT)
vext.value(0)

# Reset OLED
rst = Pin(21, Pin.OUT)
rst.value(0)
time.sleep(0.1)
rst.value(1)
time.sleep(0.1)


# I2C
i2c = SoftI2C(
    scl=Pin(18),
    sda=Pin(17),
    freq=100000
)

print("I2C devices:", i2c.scan())


# OLED
oled = SSD1306_I2C(
    128,
    64,
    i2c,
    addr=0x3c
)

oled.fill(0)

oled.text("LoRa P2P", 0, 0)
oled.text("Ready!", 0, 20)

oled.show()
