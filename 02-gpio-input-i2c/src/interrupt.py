# 이벤트 기반 #
from gpiozero import LED, Button
from signal import pause

led = LED(17)
button = Button(2)

def button_pressed():
	led.on()
	print("BUTTON PRESSED")

def button_released():
	led.off()
	print("BUTTON RELEASED")

button.when_pressed = button_pressed
button.when_released = button_released

try:
	pause()

finally:
	led.off()
	led.close()
	print("\n exit")
