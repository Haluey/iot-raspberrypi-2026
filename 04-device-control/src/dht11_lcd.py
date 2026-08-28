# pip install adafruit-circuitpython-dht
import board
import adafruit_dht

from RPLCD.i2c import CharLCD
from time import sleep

# DATA핀: GPIO4 = board.D4 = 물리핀 7번
dht = adafruit_dht.DHT11(board.D4)

lcd = CharLCD(
	i2c_expander='PCF8574',
	address=0x27,
	port=1,
	cols=16,        # 한 라인에 16글자
	rows=2,         # 2행
	charmap='A00'   # 기본 설정
)

try:
	print("DHT11 온습도 측정 시작...")

	while True:
		try:
			lcd.clear()
			temp = dht.temperature
			humi = dht.humidity

			if temp is not None and humi is not None:
				lcd.write_string(f"Temp: {temp:.1f}°C")
				lcd.crlf()
				lcd.write_string(f"Humi: {humi:.1f}%")
			else:
				lcd.write_string("Failed to measure")

		except RuntimeError as e:
			# DHT11은 가끔 읽기 실패가 정상적으로 발생함
			print("Failed, restart: ", e)

		sleep(2)

except KeyboardInterrupt:
	print("exit")

finally:
	lcd.clear()
	lcd.close(clear=True)

	dht.exit()
