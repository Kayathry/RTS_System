# import libs
from publisher import Publisher
from utils import safe_exit, create_img_dir, get_all_passwords, \
    get_existing_user_path, get_img_id_path
import RPi.GPIO as GPIO
import time
import numpy as np
import cv2 as cv
import os
import datetime

# Motion Sensor
from gpiozero import MotionSensor

# LCD
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD
lcd = LCD()

# Custom utils functions
publisher = Publisher()

# Keypad
# Define row pins to RPi (4 left most pins)
R1 = 6
R2 = 13
R3 = 19
R4 = 26
# Define column pins to RPi (4 right mos pins)
C1 = 12
C2 = 16
C3 = 20
C4 = 21
# Set in, out pin states
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


for i in [C1, C2, C3, C4]:
    GPIO.add_event_detect(i, GPIO.RISING, callback=keypad_callback)

# Motion Sensor Pin Setup
PIR_PIN = 4
pir = MotionSensor(PIR_PIN)

# Keypad Vars
keypad_pressed = -1  # set to channel if pressed

passwords, id_name_dict = get_all_passwords()
input_str = ""
checked_password = False

#Recognizer
recognizer = cv.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
# Detector
face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')

font = cv.FONT_HERSHEY_SIMPLEX

names = list(id_name_dict.values())
names.insert(0, "None")

cap = cv.VideoCapture(0)
img_dir = 'user/database'

create_img_dir(img_dir)


def set_all_line_states(state):
    for row in [R1, R2, R3, R4]:
        GPIO.output(row, state)


def check_password():
    global input_str
    global checked_password
    reset_pressed = False

    GPIO.output(R3, GPIO.HIGH)

    if (GPIO.input(C4) == 1):
        print("Input reset!")
        reset_pressed = True

    GPIO.output(R3, GPIO.LOW)
    GPIO.output(R1, GPIO.HIGH)

    if (not reset_pressed and GPIO.input(C4) == 1):
        dt = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if input_str in passwords.values():
            print("Password is correct")
            checked_password = True
            lcd.text("Verified!", 1)
            time.sleep(2)
            user_id = list(passwords.keys())[list(passwords.values()).index(input_str)]
            publisher.publish_msg(topic="RTS/verifiedMsg", 
                                     message=f"{str(user_id)}-{dt}-{'True'}")

        else:
            print("Password is incorrect")
            checked_password = False
            publisher.publish_msg(topic="RTS/verifiedMsg", 
                                     message=f"{'unknown'}-{dt}-{'False'}")

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
    if (GPIO.input(C1) == 1):
        print(chars[0])
        input_str += chars[0]
    if (GPIO.input(C2) == 1):
        print(chars[1])
        input_str += chars[1]
    if (GPIO.input(C3) == 1):
        print(chars[2])
        input_str += chars[2]
    if (GPIO.input(C4) == 1):
        print(chars[3])
        input_str += chars[3]
    GPIO.output(line, GPIO.LOW)


if not cap.isOpened():
    print("Cannot open camera")
    exit()

incorrect_count = 0
is_wait_for_motion = True
save_detected_face = True
detected_face_count = 0
# is_recognized = False
# recognised_count = 1
# prev_id = None
detected_list = []
img_id, img_path = get_img_id_path(id_name_dict)

lcd.text("Starting...", 1)
time.sleep(3)
lcd.text("Waiting for movements...", 1)

while True:
    try:
        if is_wait_for_motion:
            pir.wait_for_motion()
        if pir.motion_detected and incorrect_count < 2:
            print("Motion Detected!")
            lcd.clear()
            lcd.text("Motion Detected!", 1)
            time.sleep(3)

            signal(SIGTERM, safe_exit)
            signal(SIGHUP, safe_exit)
            lcd.text("Password:", 1)

            while not checked_password and incorrect_count < 2:
                if keypad_pressed != -1:
                    set_all_line_states(GPIO.HIGH)
                    if GPIO.input(keypad_pressed) == 0:
                        keypad_pressed = -1
                    else:
                        time.sleep(0.1)

                else:
                    if not check_password():
                        read_line(R1, ["1", "2", "3", "A"])
                        read_line(R2, ["4", "5", "6", "B"])
                        read_line(R3, ["7", "8", "9", "C"])
                        read_line(R4, ["*", "0", "#", "D"])

                        if len(input_str) != 0:
                            lcd.text("*"*len(input_str), 2)
                        time.sleep(0.1)
                    elif incorrect_count < 2:
                        if checked_password:
                            raise Exception("User Verified!")
                        incorrect_count += 1
                        lcd.clear()
                        lcd.text("Password:", 1)
                        time.sleep(0.1)

        if incorrect_count == 2:
            is_wait_for_motion = False

            ret, frame = cap.read()

            if not ret:
                print("Can't receive frame. Exiting...")
                break
            
            # frame = cv.flip(frame, -1)
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

            print("Found {0} Faces!".format(len(faces)))
            lcd.clear()
            lcd.text("Detecting Face!", 1)
        

            for (x, y, w, h) in faces:
                cv.rectangle(frame, (x-20, y-20),
                             (x+w+20, y+h+20), (0, 255, 0), 2)
                
                id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
                confidence = 100 - confidence
                if (confidence > 50):
                    id = names[id]
                    confidence = "  {0}%".format(round(confidence))
                    path = get_existing_user_path(id_name_dict, id)
                    msg_dsp = "Face Verified!"
                else:
                    id = "unknown"
                    confidence = "  {0}%".format(round(confidence))
                    path = img_path
                    msg_dsp = "Face Not Verified!"

                detected_list.append(id)
                mode_id = max(set(detected_list), key=detected_list.count)

                if len(detected_list) % 5 == 0:
                    cv.putText(frame, str(mode_id), (x+5,y-5), font, 1, (255,255,255), 2)
                    cv.putText(frame, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)

                # if detected_face_count < 30:
                #     detected_face_count += 1
                # else:
                #     save_detected_face = False

                # if id == "unknown" and save_detected_face:
                if detected_face_count < 30:
                    if save_detected_face:
                        roi_face = gray[y:y + h, x:x + w]
                        cv.imwrite(os.path.join(img_path,str(detected_face_count)+'.jpg'), 
                                roi_face)
                        print("Face saved locally.")
                    detected_face_count += 1
                else:
                    save_detected_face = False
                
                # prev_id = id

                # if prev_id == id:
                #     print(prev_id)
                #     recognised_count += 1
                # else:
                #     recognised_count = 1

                if len(detected_list) == 30:
                    dt = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    publisher.publish_msg(topic="RTS/recognizedMsg", 
                                        message=f"{dt}-{path}-{mode_id}-{mode_id}")
                    lcd.clear()
                    lcd.text(msg_dsp, 1)
                    print(msg_dsp)
                    time.sleep(1)
                    if id == "unknown":
                        lcd.clear()
                        lcd.text("Alert! Unauthorized entry!", 1)
                    raise Exception(msg_dsp)              
                
            cv.imshow('Output', frame)
            time.sleep(0.1)
            if cv.waitKey(1) == ord('q'):
                raise KeyboardInterrupt

        # pir.wait_for_no_motion()

    except KeyboardInterrupt:
        cap.release()
        cv.destroyAllWindows()
        lcd.clear()
        lcd.text("Stopped!", 1)
        time.sleep(3)
        lcd.clear()
        break

    except Exception as ex:
        print(ex)
        lcd.clear()
        incorrect_count = 0
        is_wait_for_motion = True
        save_detected_face = True
        detected_face_count = 0
        time.sleep(1)
        lcd.text("Waiting for movements...", 1)
        input_str = ""
        checked_password = False
        keypad_pressed = -1
        prev_id = None
        detected_list = []
        img_id, img_path = get_img_id_path(id_name_dict)
        cv.destroyAllWindows()

