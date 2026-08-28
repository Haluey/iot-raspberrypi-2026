from RPLCD.i2c import CharLCD
from gpiozero import DistanceSensor
from time import sleep
import statistics

lcd = CharLCD(
	i2c_expander='PCF8574',
	address=0x27,
	port=1,
	cols=16,	# 한 라인에 16글자
	rows=2,		# 2행
	charmap='A00'	# 기본 설정
)
sensor = DistanceSensor(echo=23, trigger=24)

def get_distance_cm(samples=5):
	values = []
	for _ in range(samples):
		values.append(sensor.distance * 100)
		sleep(0.05)
	return statistics.median(values)

try:
	for i in range(10):
		lcd.clear()
		dist = get_distance_cm()
		lcd.write_string(f"dist: {dist:.2f}cm")
		sleep(1.5)

finally:
	lcd.clear()
	lcd.close(clear=True)
