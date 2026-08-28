from gpiozero import DistanceSensor
from signal import pause

sensor = DistanceSensor(
	echo=23,
	trigger=24,
	threshold_distance=0.3
)

# interrupt 방식
sensor.when_in_range = lambda: print("30cm 이내 접근!")	# lambda함수는 짧게 쓰는 함수
sensor.when_out_of_range = lambda: print("멀어짐")

try:
	pause()

except KeyboardInterrupt:
	sensor.close()
