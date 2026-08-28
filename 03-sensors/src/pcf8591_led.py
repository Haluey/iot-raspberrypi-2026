import smbus
import time
from gpiozero import LED

bus = smbus.SMBus(1)
ADDR = 0x48

A0 = 0x40
A1 = 0x41
A2 = 0x42
A3 = 0x43

led = LED(17)

def read_cds():
	bus.write_byte(ADDR, A0)	# A1N0
	bus.read_byte(ADDR)			# dummy
	return bus.read_byte(ADDR)

# 기준값 설정
first = read_cds()
min_val = first
max_val = first

try:
	while True:
		val = read_cds()

		if val < min_val:
			min_val = val

		if val > max_val:
			max_val = val

		# 0으로 나누기 방지
		if max_val == min_val:
			cds_percent = 0

		else:
			cds_percent = (val - min_val) / (max_val - min_val) * 100

		cds_percent = int(cds_percent)

		print("CDS: ", cds_percent)

		# 어두워지면 LED ON
		if cds_percent < 30:
			led.off()
		else:
			led.on()

		time.sleep(0.5)

except KeyboardInterrupt:
	led.on()
	print("종 료")
