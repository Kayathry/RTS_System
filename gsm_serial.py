import serial   
import os, time

 # Enable Serial Communication
port = serial.Serial('/dev/ttyS0', baudrate=115200, timeout=1)

def serial_com(msg):
   
    port.write(str.encode('AT'+'\r\n'))
    rcv = port.readline()
    print(rcv)

    port.write(str.encode('AT+CMGF=1'+'\r\n')) # Select Message format as Text mode
    rcv = port.readline()
    print(rcv)
    time.sleep(1)

    # Sending a message to a particular Number
    port.write(str.encode('AT+CMGS="+94777479780"'+'\r\n'))
    rcv = port.readline()
    print(rcv)
    time.sleep(1)

    port.write(str.encode(msg+'\r\n'))  # Message
    rcv = port.readline()
    print(rcv)

    port.write(str.encode("\x1A")) # Enable to send SMS
    for i in range(10):
        rcv = port.readline()
        print(rcv)

# serial_com(msg='Unauthorized entry at dt')