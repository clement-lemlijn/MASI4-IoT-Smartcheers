import os
import serial
ser = serial.Serial('/dev/ttyUSB0')
ser.baudrate = 9600
ser.bytesize = 8
ser.parity = 'N'
ser.stopbits = 1
ser.timeout = None
ser.xonxoff = 0
ser.rtscts = 0

while True:
    if ser.inWaiting()>0:
        data=ser.readline()
        print("donnees recues",data)

