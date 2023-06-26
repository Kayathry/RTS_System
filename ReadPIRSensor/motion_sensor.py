from gpiozero import MotionSensor

PIR_PIN = 4
pir = MotionSensor(PIR_PIN)

while True:
	pir.wait_for_motion()
	print("You Moved")
	pir.wait_for_no_motion()
