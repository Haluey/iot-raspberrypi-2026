# Half-step: 1회전 2048 step
from gpiozero import DigitalOutputDevice
import time

# GPIO 설정 (GPIO pin)
pins = [
	DigitalOutputDevice(17),
	DigitalOutputDevice(27),
	DigitalOutputDevice(22),
	DigitalOutputDevice(23)
]

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

def rotate_steps(steps, delay=0.002):
	for _ in range(steps):
		for pattern in SEQ:
			for pin, val in zip(pins, pattern):
				pin.value = val
			time.sleep(delay)

try:
	print("90도 회전 시작")

	# 90도 = 2048 / 4 ≈ 512 step
	rotate_steps(512)

	print("완료")

except KeyboardInterrupt:
	print("중단")

finally:
	for pin in pins:
		pin.off()
