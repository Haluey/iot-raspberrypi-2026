# NER-1184 KEYPAD 4x4
from gpiozero import DigitalOutputDevice, Button
from time import sleep

# 키패드 배열
KEYS = [
	['1', '2', '3', 'A'],
	['4', '5', '6', 'B'],
	['7', '8', '9', 'C'],
	['*', '0', '#', 'D']
]

# BCM GPIO 번호 기준
ROW_PINS = [5, 6, 13, 19]       # IN0, IN1, IN2, IN3
COL_PINS = [21, 20, 16, 12]		# OUT3, OUT2, OUT1, OUT0

# 행은 출력
rows = [DigitalOutputDevice(pin, active_high=True, initial_value = False)
		for pin in ROW_PINS]

# 열은 입력, 풀다운
cols = [Button(pin, pull_up=False)
		for pin in COL_PINS]

def scan_keypad():
	for row_index, row in enumerate(rows):
		# 모든 행 LOW
		for r in rows:
			r.off()

		# 현재 형만 HIGH
		row.on()
		sleep(0.001)

		# 열 확인
		for col_index, col in enumerate(cols):
			if col.is_pressed:
				return KEYS[row_index][col_index]
	return None

try:
	last_key = None
	while True:
		key = scan_keypad()

		if key is not None and key != last_key:
			print("Pressed: ", key)
			last_key = key

		if key is None:
			last_key = None

		sleep(0.05)

except KeyboardInterrupt:
	print("Exit")

finally:
	for r in rows:
		r.off()
