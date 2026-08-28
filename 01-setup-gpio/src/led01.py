from gpiozero import LED
from time import sleep

led = [LED(14), LED(15), LED(18)]

while True:
	for i in range(3):
		led[i].on()
		sleep(0.5)
		led[i].off()
