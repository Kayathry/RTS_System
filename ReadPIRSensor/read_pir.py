import RPi.GPIO as GPIO
import time

PIR_PIN = 7
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIR_PIN, GPIO.IN)        #Read output from PIR motion sensor


while True:
    i=GPIO.input(PIR_PIN)
    if i==0:  # PIR output is LOW               
        print("No intruders",i)
        time.sleep(0.1)
    elif i==1: # PIR output is HIGH
        print("Intruder detected",i)
        time.sleep(0.1)
