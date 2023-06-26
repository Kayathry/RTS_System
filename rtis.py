# import libs
import RPi.GPIO as GPIO
import time
import numpy as np
import cv2 as cv

# Motion Sensor
from gpiozero import MotionSensor

# LCD
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD
lcd = LCD()

# Custom utils functions
from utils import safe_exit

# Keypad
## Define row pins to RPi (4 left most pins)
R1 = 6
R2 = 13
R3 = 19
R4 = 26
## Define column pins to RPi (4 right mos pins)
C1 = 12
C2 = 16
C3 = 20
C4 = 21
## Set in, out pin states
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(R1, GPIO.OUT)
GPIO.setup(R2, GPIO.OUT)
GPIO.setup(R3, GPIO.OUT)
GPIO.setup(R4, GPIO.OUT)

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def keypad_callback(key):
    global keypad_pressed
    if keypad_pressed == -1:
        keypad_pressed = key
        
for i in [C1,C2,C3,C4]:
    GPIO.add_event_detect(i, GPIO.RISING,callback=keypad_callback)

# Motion Sensor Pin Setup
PIR_PIN = 4
pir = MotionSensor(PIR_PIN)

# Keypad Vars
keypad_pressed = -1 # set to channel if pressed
password = "1436#"
input_str = ""
checked_password = False

face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
cap = cv.VideoCapture(0)

def set_all_line_states(state):
    for row in [R1,R2,R3,R4]:
        GPIO.output(row, state)


def check_password():
    global input_str
    global checked_password
    reset_pressed = False

    GPIO.output(R3, GPIO.HIGH)

    if (GPIO.input(C4) == 1):
        print("Input reset!");
        reset_pressed = True
    
    GPIO.output(R3, GPIO.LOW)
    GPIO.output(R1, GPIO.HIGH)

    if (not reset_pressed and GPIO.input(C4)==1):
        if input_str == password:
            print("Password is correct")
            checked_password = True
            lcd.text("Verified!" , 1)
            time.sleep(2)
        else:
            print("Password is incorrect")
            checked_password = False
        
        reset_pressed = True

    GPIO.output(R3, GPIO.LOW)

    if reset_pressed:
        input_str = ""

    return reset_pressed


def read_line(line, chars):
    """
    Prints the pressed key
    input: line(row pressed), characters belongs to the line
    """
    global input_str
    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        print(chars[0])
        input_str +=  chars[0]
    if(GPIO.input(C2) == 1):
        print(chars[1])
        input_str +=  chars[1]
    if(GPIO.input(C3) == 1):
        print(chars[2])
        input_str += chars[2]
    if(GPIO.input(C4) == 1):
        print(chars[3])
        input_str += chars[3]
    GPIO.output(line, GPIO.LOW)
    
if not cap.isOpened():
    print("Cannot open camera")
    exit()

incorrect_count = 0
is_wait_for_motion = True
lcd.text("Starting..." , 1)
time.sleep(3)

while True:
	try:
		if is_wait_for_motion:
			pir.wait_for_motion()
		if pir.motion_detected and incorrect_count < 2:
			print("Motion Detected!")
			lcd.text("Motion Detected!" , 1)
			time.sleep(3)
			
			signal(SIGTERM, safe_exit)
			signal(SIGHUP, safe_exit)
			lcd.text("Password:" , 1)
			print("P1")
			
			while not checked_password and incorrect_count < 2:
				if keypad_pressed != -1:
					set_all_line_states(GPIO.HIGH)
					if GPIO.input(keypad_pressed) == 0:
						keypad_pressed = -1
					else:
						time.sleep(0.1)

				else:
					if not check_password():
						read_line(R1, ["1","2","3","A"])
						read_line(R2, ["4","5","6","B"])
						read_line(R3, ["7","8","9","C"])
						read_line(R4, ["*","0","#","D"])
						
						if len(input_str) != 0:
							lcd.text("*"*len(input_str) , 2)
						time.sleep(0.1)
					elif incorrect_count<2:
						incorrect_count += 1
						lcd.clear()
						lcd.text("Password:" , 1)
						print("P2")
						time.sleep(0.1)
                        
		if incorrect_count == 2:
			is_wait_for_motion = False
			
			print(checked_password, incorrect_count)
			ret, frame = cap.read()
				
			if not ret:
				print("Can't receive frame. Exiting...")
				break
			    
			gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
			faces = face_cascade.detectMultiScale(gray,scaleFactor=1.3,minNeighbors=3,minSize=(30, 30))
			
			print("Found {0} Faces!".format(len(faces)))
			lcd.clear()
			lcd.text("Detecting Face!" , 1)
			lcd.text("Found {0}".format(len(faces)) , 2)
				
			for (x, y, w, h) in faces:
				cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
					
			cv.imshow('frame', frame)
			if cv.waitKey(1) == ord('q'):
				break
						
		#pir.wait_for_no_motion()	
			
	except KeyboardInterrupt:
		cap.release()
		cv.destroyAllWindows()
		lcd.clear()
		lcd.text("Stopped!" , 1)
		time.sleep(3)
		lcd.clear()
		break

		
	
