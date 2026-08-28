# Half-step: 360도 2048, 90도 512, 45도 256 step
from gpiozero import DigitalOutputDevice, Button
from signal import pause
import time

# 버튼 핀 설정
forward_button = Button(26, bounce_time=0.05)
reverse_button = Button(6, bounce_time=0.05)

# 모터 핀 설정
motor_pins = [
	DigitalOutputDevice(17),  # IN1
	DigitalOutputDevice(27),  # IN2
	DigitalOutputDevice(22),  # IN3
	DigitalOutputDevice(23)   # IN4
]

# Half-step 시퀀스
HALF_STEP_SEQUENCE = [
	[1, 0, 0, 0],
	[1, 1, 0, 0],
	[0, 1, 0, 0],
	[0, 1, 1, 0],
	[0, 0, 1, 0],
	[0, 0, 1, 1],
	[0, 0, 0, 1],
	[1, 0, 0, 1]
]

STEPS_90_DEGREES = 512
STEP_DELAY = 0.002

def set_motor_pins(sequence):
    for pin, value in zip(motor_pins, sequence):
        pin.value = value

def step_forward():
	for sequence in HALF_STEP_SEQUENCE:
		set_motor_pins(sequence)
		time.sleep(STEP_DELAY)

def step_reverse():
	for sequence in reversed(HALF_STEP_SEQUENCE):
		set_motor_pins(sequence)
		time.sleep(STEP_DELAY)

def rotate_forward():
	print("정방향 회전")
	for _ in range(STEPS_90_DEGREES):
		step_forward()

def rotate_reverse():
	print("역방향 회전")
	for _ in range(STEPS_90_DEGREES):
		step_reverse()

forward_button.when_pressed = rotate_forward
reverse_button.when_pressed = rotate_reverse

try:
	pause()

except KeyboardInterrupt:
	print("중단")

finally:
	for pin in motor_pins:
		pin.off()
