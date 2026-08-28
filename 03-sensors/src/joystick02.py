import smbus
import time
from gpiozero import Button

bus = smbus.SMBus(1)
ADDR = 0x48

button = Button(17)

def read_analog(channel):
	# channel: 0 ~ 3
	bus.write_byte(ADDR, 0x40 | channel)
	bus.read_byte(ADDR)	# dummy read

	return bus.read_byte(ADDR)

while True:
	x = read_analog(0)	# VRX
	y = read_analog(1)	# VRY
	sw = button.is_pressed

	print(f"X: {x}, Y: {y}, SW: {sw}")

	if x > 200:
		print("RIGHT")
	elif x < 50:
		print("LEFT")

	if y > 210:
		print("DOWN")
	elif y < 50:
		print("UP")

	if 110 < x < 185:	# 안정화 (데드존 필요)
		print("CENTER")

	time.sleep(0.5)
