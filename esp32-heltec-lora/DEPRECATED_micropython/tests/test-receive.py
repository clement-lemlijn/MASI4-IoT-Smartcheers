from sx126x import SX126X, SX126X_MAX_PACKET_LENGTH, ERR_NONE
import time


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

radio.setRfFrequency(868100000)

radio.begin(
    bw=125,
    sf=7,
    cr=5,
    syncWord=1,
    currentLimit=140,
    preambleLength=8,
    tcxoVoltage=1.8
)

print("LoRa prêt")

radio.startReceive()

print("En écoute...")

buffer = bytearray(SX126X_MAX_PACKET_LENGTH)



    
    
while True:

    irq = radio.getIrqStatus()

    if irq:
        print("IRQ:", hex(irq))

    data = radio.receive(
        buffer,
        255,
        False,
        0
    )

    if data:
        print("Reçu :", data)

    time.sleep(0.1)    

