from gpiozero import DigitalOutputDevice, Button, LED, PWMOutputDevice
from RPLCD.i2c import CharLCD
from time import sleep

IN1 = DigitalOutputDevice(23)
IN2 = DigitalOutputDevice(24)
IN3 = DigitalOutputDevice(25)
IN4 = DigitalOutputDevice(26)

KEYS = [
	['1', '2', '3', 'A'],
	['4', '5', '6', 'B'],
	['7', '8', '9', 'C'],
	['*', '0', '#', 'D']
]

ROW_PINS = [5, 6, 13, 19]       # IN0, IN1, IN2, IN3
COL_PINS = [21, 20, 16, 12]		# OUT3, OUT2, OUT1, OUT0

rows = [DigitalOutputDevice(pin, active_high=True, initial_value = False)
		for pin in ROW_PINS]

cols = [Button(pin, pull_up=False)
		for pin in COL_PINS]

lcd = CharLCD(
	i2c_expander='PCF8574',
	address=0x27,
	port=1,
	cols=16,
	rows=2,
	charmap='A00'
)

led = LED(17)
buzzer = PWMOutputDevice(18)

# 모터 시퀀스
SEQ = [
	[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],
	[0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1]
]

motor_pins = [IN1, IN2, IN3, IN4]

PASSWORD = "123456"
MAX_PASSWORD_LENGTH = 6

change_mode = False
verify_mode = False

def set_motor(seq):
	for pin, val in zip(motor_pins, seq):
		pin.value = val

def step_forward(delay=0.002):
	for seq in SEQ:
		set_motor(seq)
		sleep(delay)

def step_reverse(delay=0.002):
	for seq in reversed(SEQ):
		set_motor(seq)
		sleep(delay)

def motor_open():
	print("문 열림")
	for _ in range(512):   # 열기
		step_forward()

	stop_motor()

def motor_close():
	print("문 닫힘")
	for _ in range(512):   # 닫기
		step_reverse()

	stop_motor()

def stop_motor():
	for pin in motor_pins:
		pin.off()

def play_tone(freq, duration):
	buzzer.frequency = freq
	buzzer.value = 0.1
	sleep(duration)
	buzzer.off()
	sleep(0.05)

def beep_fail():
	play_tone(880, 0.15)
	sleep(0.05)
	play_tone(880, 0.15)
	sleep(0.05)
	play_tone(523, 0.4)

def beep_success():
	play_tone(1046, 0.1)
	#play_tone(1318, 0.1)
	play_tone(1567, 0.1)
	play_tone(2093, 0.2)

def scan_keypad():
	for row_index, row in enumerate(rows):
		for r in rows:
			r.off()

		row.on()
		sleep(0.001)

		for col_index, col in enumerate(cols):
			if col.is_pressed:
				return KEYS[row_index][col_index]
	return None

def display_message(line1, line2=""):
	lcd.clear()
	lcd.cursor_pos = (0, 0)
	lcd.write_string(line1[:16])
	lcd.cursor_pos = (1, 0)
	lcd.write_string(line2[:16])

def display_password(input_password):
	hidden = "*" * len(input_password)
	if change_mode and verify_mode:
		display_message("Old Password", hidden)
	elif change_mode and not verify_mode:
		display_message("New Password", hidden)
	else:
		display_message("Enter Password", hidden)

def check_password(input_password):
	return input_password == PASSWORD

def handle_key(key, input_password):
	global PASSWORD, change_mode, verify_mode

	play_tone(1200, 0.03)

	# # 누르면 비밀번호 변경 시작
	if key == '#' and not change_mode:
		change_mode = True
		verify_mode = True
		display_message("Change Mode", "Old Password")
		sleep(1)
		return ""

	# D 누르면 한 글자 삭제
	if key == 'D':
		return input_password[:-1]

	# 숫자 입력
	if key.isdigit():
		if len(input_password) < MAX_PASSWORD_LENGTH:
			return input_password + key
		else:
			display_message("Max 6 digits", "Press *")
			sleep(1)
			return input_password

	# * 누르면 확인
	if key == '*':
		if len(input_password) != MAX_PASSWORD_LENGTH:
			display_message("Need 6 digits", "Try Again")
			sleep(1.5)
			return ""

		# 1단계: 기존 비밀번호 확인
		if change_mode and verify_mode:
			if check_password(input_password):
				verify_mode = False
				display_message("New Password", "Enter 6 digits")
				beep_success()

			else:
				change_mode = False
				verify_mode = False
				display_message("Wrong Password", "Cancel Change")
				beep_fail()

			sleep(1.5)
			return ""

		# 2단계: 새 비밀번호 저장
		if change_mode and not verify_mode:
			PASSWORD = input_password
			change_mode = False
			display_message("Password", "Changed")
			beep_success()
			sleep(1.5)
			return ""

		# 일반 도어락 모드
		if check_password(input_password):
			display_message("Password OK", "Unlocked")
			beep_success()
			led.off()
			motor_open()

			sleep(5)
			motor_close()

		else:
			display_message("Password Fail", "Try Again")
			beep_fail()

		sleep(1.5)
		return ""

	return input_password

try:
	last_key = None
	input_password = ""
	led.on()

	display_message("Password System", "Ready")
	sleep(1)
	display_password(input_password)

	while True:
		led.on()
		key = scan_keypad()

		if key is not None and key != last_key:
			print("Pressed: ", key)

			input_password = handle_key(key, input_password)
			display_password(input_password)

			last_key = key

		if key is None:
			last_key = None

		sleep(0.05)

except KeyboardInterrupt:
	print("Exit")

finally:
	lcd.clear()
	lcd.close(clear=True)
	led.on()

	for r in rows:
		r.off()
