from machine import UART, Pin
import time


uart = UART(
    2,
    baudrate=115200,
    tx=17,
    rx=16
)


print("ESP32 VROOM UART RECEIVER")


while True:

    if uart.any():

        data = uart.read()

        if data:
            print("RX :", data.decode())


    time.sleep(0.1)
