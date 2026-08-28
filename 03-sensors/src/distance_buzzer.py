from gpiozero import DistanceSensor, PWMOutputDevice
from time import sleep
import statistics

sensor = DistanceSensor(echo=23, trigger=24)
buzzer = PWMOutputDevice(17)

def get_distance_cm(samples=5):
	values = []
	for _ in range(samples):
		values.append(sensor.distance * 100)
		sleep(0.05)
	return statistics.median(values)

# 부드러운 값용
smooth_dist = get_distance_cm()

def smooth(val, prev, alpha=0.3):
	return alpha * val + (1 - alpha) * prev

try:
	while True:
		raw = get_distance_cm()

		# 값 부드럽게 만들기
		smooth_dist = smooth(raw, smooth_dist)

		print(f"거리(평균): {smooth_dist:.2f}cm")

		# 30cm 이상이면 소리 끄기
		if smooth_dist > 30:
			buzzer.off()
			sleep(0.2)
			continue

		# 너무 가까우면 연속음
		if smooth_dist < 3:
			buzzer.frequency = 1000
			buzzer.value =  0.5
			sleep(0.05)
			continue


		# 3~30cm: 가까울수록 빠르게
		norm = min(max(smooth_dist / 30, 0), 1)
		delay = (norm ** 2) * 0.5 + 0.002	# 거리 -> 시간으로 변환

		buzzer.frequency = 1000
		buzzer.value = 0.5
		sleep(0.02)

		buzzer.off()
		sleep(delay)

except KeyboardInterrupt:
	pass

finally:
	buzzer.off()
	buzzer.close()
	sensor.close()
