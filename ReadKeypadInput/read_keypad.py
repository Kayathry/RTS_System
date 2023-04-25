# import libs
import RPi.GPIO as GPIO
import time

#Define row pins to RPi (4 left most pins)
R1 = 5 
R2 = 6
R3 = 13
R4 = 19

# Define column pins ti RPi (4 right mos pins)
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

keypad_pressed = -1 # set to channel if pressed

password = "1234#"

input_str = ""

def keypad_callback(key):
    global keypad_pressed
    if keypad_pressed == -1:
        keypad_pressed = key


for i in [C1,C2,C3,C4]:
    GPIO.add_event_detect(i, GPIO.RISING,callback=keypad_callback)

def set_all_line_states(state):
    for row in [R1,R2,R3,R4]:
        GPIO.output(row, state)


def check_password():
    global input_str
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
        else:
            print("Password is incorrect")

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

try:
    while True:
       
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
                time.sleep(0.1)
            else:
                time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopped!")
