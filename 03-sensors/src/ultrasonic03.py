from gpiozero import DistanceSensor
from time import sleep
import statistics

sensor = DistanceSensor(echo=23, trigger=24)

def get_distance_cm(samples=5):
	values = []
	for _ in range(samples):
		values.append(sensor.distance * 100)
		sleep(0.05)
	return statistics.mean(values)

try:
	while True:
		dist = get_distance_cm()
		print(f"거리(평균): {dist:.2f}cm")
		sleep(0.5)

except KeyboardInterrupt:
	pass

finally:
	sensor.close()
