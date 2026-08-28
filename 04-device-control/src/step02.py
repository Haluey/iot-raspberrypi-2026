# Half-step: 360도 2048, 90도 512, 45도 256 step
from gpiozero import DigitalOutputDevice
import time

# GPIO 설정 (GPIO pin)
IN1 = DigitalOutputDevice(17)
IN2 = DigitalOutputDevice(27)
IN3 = DigitalOutputDevice(22)
IN4 = DigitalOutputDevice(23)

# Half-step 시퀀스 (표준)
SEQ = [
	[1, 0, 0, 0],
	[1, 1, 0, 0],
	[0, 1, 0, 0],
	[0, 1, 1, 0],
	[0, 0, 1, 0],
	[0, 0, 1, 1],
	[0, 0, 0, 1],
	[1, 0, 0, 1]
]

pins = [IN1, IN2, IN3, IN4]

def step(delay=0.002):
	for seq in SEQ:
		for pin, val in zip(pins, seq):
			if val:
				pin.on()
			else:
				pin.off()
		time.sleep(delay)

def step_reverse(delay=0.002):
	for seq in reversed(SEQ):
		for pin, val in zip(pins, seq):
			if val:
				pin.on()
			else:
				pin.off()
		time.sleep(delay)

try:
	print("정방향  회전")
	for _ in range(512):	# 약 1회전
		step()

	time.sleep(1)

	print("역방향 회전")
	for	_ in range(512):
		step_reverse()

	print("완료")

except KeyboardInterrupt:
	print("중단")

finally:
	for pin in pins:
		pin.off()

