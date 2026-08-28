import smbus
import time
from gpiozero import Button

bus = smbus.SMBus(1)	# 객체 생성
ADDR = 0x48		# PCF8591 기본 주소

button = Button(17)

def read_adc(channel):
	bus.write_byte(ADDR, 0x40 | channel)
	bus.read_byte(ADDR)		# dummy read

	return bus.read_byte(ADDR)

try:
	while True:
		x = read_adc(0)
		y = read_adc(1)
		sw = button.is_pressed

		print(f"X: {x}, Y: {y}, SW: {sw}")
		time.sleep(0.5)

except KeyboardInterrupt:
	print("종료")
