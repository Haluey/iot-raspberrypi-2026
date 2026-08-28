from RPLCD.i2c import CharLCD
import time

lcd = CharLCD(
	i2c_expander='PCF8574',
	address=0x27,
	port=1,
	cols=16,	# 한 라인에 16글자
	rows=2,		# 2행
	charmap='A00'	# 기본 설정
)

try:
	for dan in range(2, 10):
		for i in range(1, 10, 2):
			lcd.clear()

			# 첫 줄
			line1 = f"{dan} X {i} = {dan * i}"
			lcd.write_string(line1.ljust(16))	# 문자열 쓰기

			# 둘째 줄
			if i + 1 < 10:
				lcd.crlf()
				line2 = f"{dan} X {i + 1} = {dan * (i + 1)}"
				lcd.write_string(line2.ljust(16))

			time.sleep(1.5)

finally:
	lcd.clear()
	lcd.close(clear=True)
