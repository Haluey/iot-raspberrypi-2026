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
	lcd.clear()
	lcd.write_string("Raspberry Pi 5")	# 문자열 쓰기
	lcd.crlf()	# 줄바꿈
	lcd.write_string("1602 LCD OK")
	#lcd.cursor_pos = (1, 0)	# 커서 위치 지정
	#lcd.display_enabled = False / True	# 디스플레이 오프
	#lcd.backlight_enabled = True / False	# 백라이트 제건

	time.sleep(20)

finally:
	lcd.clear()
	lcd.close(clear=True)
