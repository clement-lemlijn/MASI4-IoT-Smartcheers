from sx126x import SX126X
import time
from sx126x import SX126X_LORA_BW_125_0


radio = SX126X(
    spi_bus=2,
    clk=9,
    mosi=10,
    miso=11,
    cs=8,
    irq=14,
    rst=12,
    gpio=13
)

print("SX1262 créé")


# Fréquence identique au LA66
radio.setRfFrequency(868100000)


# Configuration LoRa
radio.begin(
    bw=125,
    sf=7,
    cr=5,
    syncWord=0,
    currentLimit=140,
    preambleLength=8,
    tcxoVoltage=1.8
)

print("SX1262 initialisé")
