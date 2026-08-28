import smbus
import time

bus = smbus.SMBus(1)
ADDR = 0x48

A0 = 0x40
A1 = 0x41
A2 = 0x42
A3 = 0x43

def read_cds():
	bus.write_byte(ADDR, A0)	# A1N0
	bus.read_byte(ADDR)			# dummy
	return bus.read_byte(ADDR)

# 기준값 설정
base = read_cds()

try:
	while True:
		val = read_cds()

		diff = val - base		# 변화량
		scaled = val + diff * 10	# 변화량만 10배 확대

		print("CDS: ", scaled)
		time.sleep(0.5)



except KeyboardInterrupt:
	print("종 료")
